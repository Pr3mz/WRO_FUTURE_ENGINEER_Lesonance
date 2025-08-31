import time
import cv2 as cv
import numpy as np
import torch

def load_model(model_path, device='cpu'):
    model = torch.load(model_path, map_location=device)
    model.eval()
    return model

def preprocess_image(image_path, input_size):
    image = cv.imread(image_path)
    image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
    image_resized = cv.resize(image, input_size)
    image_normalized = image_resized / 255.0
    image_transposed = np.transpose(image_normalized, (2, 0, 1))
    image_tensor = torch.tensor(image_transposed, dtype=torch.float32).unsqueeze(0)
    return image_tensor

def postprocess_output(output, conf_threshold=0.5):
    output = output[0]
    boxes = output['boxes'].detach().cpu().numpy()
    scores = output['scores'].detach().cpu().numpy()
    labels = output['labels'].detach().cpu().numpy()
    mask = scores >= conf_threshold
    return boxes[mask], scores[mask], labels[mask]

def draw_detections(image, boxes, scores, labels, class_names):
    for box, score, label in zip(boxes, scores, labels):
        x1, y1, x2, y2 = map(int, box)
        cv.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv.putText(image, f"{class_names[label]}: {score:.2f}", (x1, y1 - 10),
                   cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    return image

def main(model_path, image_path, class_names, input_size=(224, 224), conf_threshold=0.5, device='cpu'):
    model = load_model(model_path, device)
    image_tensor = preprocess_image(image_path, input_size).to(device)
    start_time = time.time()
    with torch.no_grad():
        output = model(image_tensor)
    inference_time = time.time() - start_time
    boxes, scores, labels = postprocess_output(output, conf_threshold)
    image = cv.imread(image_path)
    image_with_detections = draw_detections(image, boxes, scores, labels, class_names)
    print(f"Inference Time: {inference_time:.4f} seconds")
    cv.imshow('Detections', image_with_detections)
    cv.waitKey(0)
    cv.destroyAllWindows()

if __name__ == "__main__":
    model_path = 'path/to/your/model.pth'
    image_path = 'path/to/your/image.jpg'
    class_names = ['class1', 'class2', 'class3']  # Replace with your actual class names
    main(model_path, image_path, class_names)