# Use a pipeline as a high-level helper
from transformers import pipeline
# Load model directly
from transformers import AutoImageProcessor, AutoModelForImageClassification

def main(image_path: str = None):
    # Load the image processor and model
    processor = AutoImageProcessor.from_pretrained("kriskrishna/vit-Facial-Expression-Recognition")
    model = AutoModelForImageClassification.from_pretrained("kriskrishna/vit-Facial-Expression-Recognition")
    
    # Create a pipeline for image classification
    pipe = pipeline("image-classification", model=model, image_processor=processor)
    
    # Run classification
    results = pipe(image_path)

    # Get the label with the highest score
    best_result = max(results, key=lambda x: x['score'])

    # Return the label only if confidence > 0.5
    if best_result['score'] > 0.4:
        return best_result['label']
    else:
        return None

if __name__ == "__main__":
    max_label = main("/ai-data/sik/kgy/ml/dataset/test2.jpg")
    print(max_label)
