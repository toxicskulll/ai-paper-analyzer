import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
import time

class LaTeXFineTuner:
    """Fine-tune models for LaTeX generation"""
    
    def __init__(self, data_dir: str = "D:/hack/ai-paper-analyzer/latex"):
        self.data_dir = Path(data_dir)
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('finetune.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def validate_jsonl_format(self, file_path: str) -> bool:
        """Validate JSONL format for fine-tuning"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    data = json.loads(line.strip())
                    
                    # Check required fields
                    if 'prompt' not in data or 'completion' not in data:
                        self.logger.error(f"Line {line_num}: Missing 'prompt' or 'completion'")
                        return False
                    
                    # Check data quality
                    if len(data['prompt']) < 50:
                        self.logger.warning(f"Line {line_num}: Short prompt ({len(data['prompt'])} chars)")
                    
                    if len(data['completion']) < 100:
                        self.logger.warning(f"Line {line_num}: Short completion ({len(data['completion'])} chars)")
            
            self.logger.info(f"✅ JSONL format validation passed: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Validation failed: {e}")
            return False
    
    def convert_to_openai_format(self, input_file: str, output_file: str) -> bool:
        """Convert dataset to OpenAI fine-tuning format"""
        try:
            with open(input_file, 'r', encoding='utf-8') as infile, \
                 open(output_file, 'w', encoding='utf-8') as outfile:
                
                for line in infile:
                    data = json.loads(line.strip())
                    
                    # OpenAI format
                    openai_format = {
                        "messages": [
                            {"role": "user", "content": data['prompt']},
                            {"role": "assistant", "content": data['completion']}
                        ]
                    }
                    
                    outfile.write(json.dumps(openai_format) + '\n')
            
            self.logger.info(f"✅ Converted to OpenAI format: {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ OpenAI format conversion failed: {e}")
            return False
    
    def finetune_openai(self, train_file: str, val_file: str, model: str = "gpt-3.5-turbo-1106") -> Optional[str]:
        """Fine-tune using OpenAI API"""
        try:
            import openai
            
            # Set API key (make sure it's in your environment)
            if not os.getenv("OPENAI_API_KEY"):
                self.logger.error("❌ OPENAI_API_KEY not found in environment variables")
                return None
            
            client = openai.OpenAI()
            
            # Upload training file
            self.logger.info("📤 Uploading training file...")
            with open(train_file, "rb") as f:
                training_file = client.files.create(file=f, purpose="fine-tune")
            
            # Upload validation file
            self.logger.info("📤 Uploading validation file...")
            with open(val_file, "rb") as f:
                validation_file = client.files.create(file=f, purpose="fine-tune")
            
            # Create fine-tuning job
            self.logger.info("🚀 Starting fine-tuning job...")
            fine_tune_job = client.fine_tuning.jobs.create(
                training_file=training_file.id,
                validation_file=validation_file.id,
                model=model,
                hyperparameters={
                    "n_epochs": 3,
                    "batch_size": 1,
                    "learning_rate_multiplier": 0.1
                }
            )
            
            job_id = fine_tune_job.id
            self.logger.info(f"✅ Fine-tuning job created: {job_id}")
            
            # Monitor progress
            self.monitor_openai_job(client, job_id)
            
            return job_id
            
        except Exception as e:
            self.logger.error(f"❌ OpenAI fine-tuning failed: {e}")
            return None
    
    def monitor_openai_job(self, client, job_id: str):
        """Monitor OpenAI fine-tuning job progress"""
        self.logger.info("⏳ Monitoring fine-tuning progress...")
        
        while True:
            job = client.fine_tuning.jobs.retrieve(job_id)
            status = job.status
            
            self.logger.info(f"Job status: {status}")
            
            if status == "succeeded":
                self.logger.info(f"🎉 Fine-tuning completed! Model: {job.fine_tuned_model}")
                break
            elif status in ["failed", "cancelled"]:
                self.logger.error(f"❌ Fine-tuning {status}")
                break
            
            time.sleep(30)  # Check every 30 seconds
    
    def finetune_huggingface(self, train_file: str, val_file: str, base_model: str = "microsoft/DialoGPT-medium"):
        """Fine-tune using Hugging Face Transformers"""
        try:
            from transformers import (
                AutoTokenizer, AutoModelForCausalLM, 
                TrainingArguments, Trainer, DataCollatorForLanguageModeling
            )
            from datasets import load_dataset
            import torch
            
            self.logger.info("🤗 Starting Hugging Face fine-tuning...")
            
            # Load tokenizer and model
            tokenizer = AutoTokenizer.from_pretrained(base_model)
            model = AutoModelForCausalLM.from_pretrained(base_model)
            
            # Add padding token if not present
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            # Load datasets
            train_dataset = load_dataset('json', data_files=train_file, split='train')
            val_dataset = load_dataset('json', data_files=val_file, split='train')
            
            # Tokenization function
            def tokenize_function(examples):
                # Combine prompt and completion
                texts = [f"Prompt: {p}\n\nCompletion: {c}" for p, c in 
                        zip(examples['prompt'], examples['completion'])]
                
                return tokenizer(
                    texts,
                    truncation=True,
                    padding=True,
                    max_length=512,
                    return_tensors="pt"
                )
            
            # Tokenize datasets
            train_dataset = train_dataset.map(tokenize_function, batched=True)
            val_dataset = val_dataset.map(tokenize_function, batched=True)
            
            # Data collator
            data_collator = DataCollatorForLanguageModeling(
                tokenizer=tokenizer,
                mlm=False,
            )
            
            # Training arguments
            training_args = TrainingArguments(
                output_dir="./latex_model",
                overwrite_output_dir=True,
                num_train_epochs=3,
                per_device_train_batch_size=1,
                per_device_eval_batch_size=1,
                warmup_steps=100,
                logging_steps=10,
                save_steps=500,
                eval_steps=500,
                evaluation_strategy="steps",
                save_strategy="steps",
                load_best_model_at_end=True,
                metric_for_best_model="eval_loss",
                greater_is_better=False,
            )
            
            # Create trainer
            trainer = Trainer(
                model=model,
                args=training_args,
                data_collator=data_collator,
                train_dataset=train_dataset,
                eval_dataset=val_dataset,
            )
            
            # Start training
            self.logger.info("🚂 Starting training...")
            trainer.train()
            
            # Save model
            trainer.save_model("./latex_model_final")
            tokenizer.save_pretrained("./latex_model_final")
            
            self.logger.info("🎉 Hugging Face fine-tuning completed!")
            
        except Exception as e:
            self.logger.error(f"❌ Hugging Face fine-tuning failed: {e}")
    
    def test_model(self, model_path_or_id: str, test_prompt: str, provider: str = "huggingface"):
        """Test the fine-tuned model"""
        if provider == "openai":
            self.test_openai_model(model_path_or_id, test_prompt)
        else:
            self.test_huggingface_model(model_path_or_id, test_prompt)
    
    def test_openai_model(self, model_id: str, test_prompt: str):
        """Test OpenAI fine-tuned model"""
        try:
            import openai
            client = openai.OpenAI()
            
            response = client.chat.completions.create(
                model=model_id,
                messages=[{"role": "user", "content": test_prompt}],
                max_tokens=1000
            )
            
            self.logger.info("🧪 Test Results (OpenAI):")
            self.logger.info(f"Input: {test_prompt[:100]}...")
            self.logger.info(f"Output: {response.choices[0].message.content[:200]}...")
            
        except Exception as e:
            self.logger.error(f"❌ OpenAI model test failed: {e}")
    
    def test_huggingface_model(self, model_path: str, test_prompt: str):
        """Test Hugging Face fine-tuned model"""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch
            
            tokenizer = AutoTokenizer.from_pretrained(model_path)
            model = AutoModelForCausalLM.from_pretrained(model_path)
            
            # Prepare input
            input_text = f"Prompt: {test_prompt}\n\nCompletion:"
            inputs = tokenizer.encode(input_text, return_tensors="pt")
            
            # Generate
            with torch.no_grad():
                outputs = model.generate(
                    inputs,
                    max_length=500,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )
            
            generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            self.logger.info("🧪 Test Results (Hugging Face):")
            self.logger.info(f"Input: {test_prompt[:100]}...")
            self.logger.info(f"Output: {generated_text[len(input_text):200]}...")
            
        except Exception as e:
            self.logger.error(f"❌ Hugging Face model test failed: {e}")
    
    def run_complete_pipeline(self, provider: str = "huggingface"):
        """Run the complete fine-tuning pipeline"""
        
        self.logger.info("🚀 Starting complete fine-tuning pipeline...")
        
        # File paths
        train_file = self.data_dir / "enhanced_latex_dataset_train.jsonl"
        val_file = self.data_dir / "enhanced_latex_dataset_val.jsonl"
        
        # Validate files exist
        if not train_file.exists() or not val_file.exists():
            self.logger.error("❌ Training/validation files not found. Run enhanced_latex_generator.py first!")
            return
        
        # Validate format
        if not self.validate_jsonl_format(str(train_file)) or not self.validate_jsonl_format(str(val_file)):
            return
        
        # Choose provider
        if provider == "openai":
            # Convert to OpenAI format
            openai_train = str(train_file).replace('.jsonl', '_openai.jsonl')
            openai_val = str(val_file).replace('.jsonl', '_openai.jsonl')
            
            if self.convert_to_openai_format(str(train_file), openai_train) and \
               self.convert_to_openai_format(str(val_file), openai_val):
                
                job_id = self.finetune_openai(openai_train, openai_val)
                if job_id:
                    self.logger.info(f"✅ OpenAI fine-tuning job: {job_id}")
        
        else:  # Hugging Face
            self.finetune_huggingface(str(train_file), str(val_file))
        
        # Test with sample prompt
        test_prompt = """Generate a complete LaTeX document for an IEEE conference paper about:
        
Title: Deep Learning for Medical Image Analysis
Authors: Dr. Alice Smith, Bob Johnson
Abstract: This paper presents a novel deep learning approach for medical image analysis...
Keywords: Deep Learning, Medical Imaging, CNN
        
Sections:
- Introduction: Overview of medical imaging challenges
- Methodology: CNN architecture with attention mechanisms  
- Results: 98.5% accuracy on chest X-ray classification
- Conclusion: Superior performance compared to existing methods"""
        
        if provider == "openai":
            # You'll need to update this with the actual model ID after training
            self.logger.info("⚠️ Update model ID after OpenAI training completes")
        else:
            self.test_model("./latex_model_final", test_prompt, "huggingface")


def main():
    """Main execution function"""
    
    # Choose your provider: "openai" or "huggingface"
    PROVIDER = "huggingface"  # Change to "openai" if you prefer
    
    # Create fine-tuner
    finetuner = LaTeXFineTuner()
    
    # Run complete pipeline
    finetuner.run_complete_pipeline(provider=PROVIDER)

if __name__ == "__main__":
    main()