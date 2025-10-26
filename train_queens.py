#!/usr/bin/env python3
"""
Queens Game RL Training Script
Adapted from the 2048 RL example for server deployment on Ubuntu with MI300X GPU
"""

import os
import sys
import torch
from typing import Callable, List
from unsloth import FastLanguageModel
from trl import GRPOConfig, GRPOTrainer
from datasets import Dataset
from transformers import TextStreamer
from unsloth import execute_with_time_limit, check_python_modules, create_locked_down_function
import itertools
import time

# Add src to path
sys.path.insert(0, 'src')

from envs.queens_env import QueensEnv, QueensAction


# Configuration
MAX_SEQ_LENGTH = os.getenv('MAX_SEQ_LENGTH',default=768)
LORA_RANK = os.getenv('LORA_RANK',default=4)
MODEL_NAME = os.getenv('MODEL_NAME',default="ERROR")
HF_TOKEN = os.getenv('HF_TOKEN',default=None)
OUTPUT_DIR = os.getenv('OUTPUT_DIR',default="outputs_queens")
MAX_STEPS = os.getenv('MAX_STEPS',default=300)
BATCH_SIZE = os.getenv("BATCH_SIZE",default=1)
GRADIENT_ACCUMULATION_STEPS = os.getenv("GRADIENT_ACCUMULATION_STEPS",default=1)
NUM_GENERATIONS = os.getenv("NUM_GENERATIONS",default=1)

def setup_model():
    """Load and setup the model with LoRA"""
    global MAX_SEQ_LENGTH,LORA_RANK,MODEL_NAME,HF_TOKEN,OUTPUT_DIR,MAX_STEPS,BATCH_SIZE,GRADIENT_ACCUMULATION_STEPS,NUM_GENERATIONS    
    
    print(f"model: {MODEL_NAME}")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=MODEL_NAME,
        max_seq_length=MAX_SEQ_LENGTH,
        load_in_4bit=True,
        cache_dir='/app/cache/transformers',
        token=os.environ.get('HF_TOKEN'),
        #fast_inference = True, # Enable vLLM fast inference
        gpu_memory_utilization = 0.4,
        max_lora_rank = LORA_RANK
    )
    print('getting peft model')
    model = FastLanguageModel.get_peft_model(
        model,
        r=LORA_RANK,
        target_modules=[
             "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj",
        ],
        lora_alpha=LORA_RANK,
        use_gradient_checkpointing="unsloth",
        random_state=3407,
    )

    return model, tokenizer

def create_prompt():
    """Create the prompt for Queens strategy generation"""
    return """
Create a new short Queens strategy using only native Python code.

You are given a 2D list of integers representing the current board state:
- 0: empty cell
- 1: marked cell
- 2: queen

You are also given the regions as a 2D list of integers.

Output one action as a tuple: (cell_index, action_type)
- cell_index: 0 to grid_size*grid_size - 1 (row-major order)
- action_type: 0 (clear), 1 (mark), 2 (place queen)

Only place a queen if it's a valid move according to the rules:
- No two queens in same row, column, or region
- No two queens adjacent (including diagonally)

Output your strategy in backticks using the format below:

```python
def strategy(board, regions):
    grid_size = len(board)
    # Your strategy logic here
    return (cell_index, action_type)  # Example
```

All helper functions should be inside def strategy. Only output the short function `strategy`.
""".strip()

def extract_function(text: str):
    """Extract the strategy function from the model output"""
    if text.count("```") >= 2:
        first = text.find("```") + 3
        second = text.find("```", first)
        fx = text[first:second].strip()
        fx = fx.removeprefix("python\n")
        fx = fx[fx.find("def"):]
        if fx.startswith("def strategy(board, regions):"):
            return fx
    return None

def function_works(completions, **kwargs):
    """Reward function: check if the strategy is valid Python"""
    scores = []
    for completion in completions:
        score = 0
        response = completion[0]["content"]
        function = extract_function(response)
        if function is not None:
            ok, info = check_python_modules(function)
        if function is None or "error" in info:
            score = -2.0
        else:
            try:
                new_strategy = create_locked_down_function(function)
                score = 1.0
            except:
                score = -0.5
        scores.append(score)
    return scores

def no_cheating(completions, **kwargs):
    """Reward function: check if the function imports external modules"""
    scores = []
    for completion in completions:
        score = 0
        response = completion[0]["content"]
        function = extract_function(response)
        if function is not None:
            ok, info = check_python_modules(function)
            scores.append(1.0 if ok else -20.0)
        else:
            scores.append(-1.0)
    return scores

def strategy_succeeds(completions, **kwargs):
    """Reward function: check if the strategy solves the Queens puzzle"""
    scores = []
    global PRINTER
    PRINTER = 0

    for completion in completions:
        printed = False
        score = 0
        response = completion[0]["content"]
        function = extract_function(response)

        if PRINTER % 5 == 0:
            printed = True
            print(function)
        PRINTER += 1

        if function is None:
            scores.append(0)
            continue

        try:
            new_strategy = create_locked_down_function(function)
        except:
            scores.append(0)
            continue

        try:
            # Create environment with random level
            env = QueensEnv()
            obs = env.reset(grid_size=8)  # Use 8x8 for training

            steps = 0
            max_steps = 50  # Limit steps to prevent infinite loops

            while not obs.done and steps < max_steps:
                try:
                    with execute_with_time_limit(5):
                        action = new_strategy(obs.board, obs.regions)
                        if not isinstance(action, tuple) or len(action) != 2:
                            break
                        cell_index, action_type = action
                        if not (0 <= cell_index < 64 and 0 <= action_type <= 2):
                            break

                        action_obj = QueensAction(cell_index=cell_index, action_type=action_type)
                        obs = env.step(action_obj)
                        steps += 1

                except:
                    break

            if obs.done:
                scores.append(20.0)  # Success!
            else:
                scores.append(2.0)  # Partial progress

        except Exception as e:
            print(f"Exception: {str(e)}")
            scores.append(-3.0)

    return scores

def main():
    global MAX_SEQ_LENGTH,LORA_RANK,MODEL_NAME,HF_TOKEN,OUTPUT_DIR,MAX_STEPS,BATCH_SIZE,GRADIENT_ACCUMULATION_STEPS,NUM_GENERATIONS    
    
    """Main training function"""
    print("Setting up model...")
    model, tokenizer = setup_model()

    print("Creating prompt...")
    prompt = create_prompt()

    print("Creating dataset...")
    dataset = Dataset.from_list([
        {"prompt": [{"role": "user", "content": prompt.strip()}], "answer": 0, "reasoning_effort": "low"}
    ] * 1000)

    max_prompt_length = len(tokenizer.apply_chat_template(
        [{"role": "user", "content": prompt.strip()}],
        add_generation_prompt=True
    ))
    max_completion_length = MAX_SEQ_LENGTH - max_prompt_length

    print("Setting up training arguments...")
    training_args = GRPOConfig(
        temperature=1.0,
        learning_rate=5e-5,
        weight_decay=0.01,
        warmup_ratio=0.1,
        lr_scheduler_type="linear",
        optim="adamw_8bit",
        logging_steps=1,
        per_device_train_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,
        num_generations=NUM_GENERATIONS,
        max_prompt_length=max_prompt_length,
        max_completion_length=max_completion_length,
        max_steps=MAX_STEPS,
        save_steps=50,
        report_to="trackio",
        output_dir=OUTPUT_DIR,
    )

    print("Setting up trainer...")
    trainer = GRPOTrainer(
        model=model,
        processing_class=tokenizer,
        reward_funcs=[
            function_works,
            no_cheating,
            strategy_succeeds,
        ],
        args=training_args,
        train_dataset=dataset,
    )

    print("Starting training...")
    trainer.train()

    print("Training completed!")

    # Save the model
    model.save_pretrained_merged("queens_finetuned_model", tokenizer, save_method="merged_16bit")

if __name__ == "__main__":
    main()
