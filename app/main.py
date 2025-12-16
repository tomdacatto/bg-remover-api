from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import io
from PIL import Image
import rembg

app = FastAPI(
    title="BG Remover API",
    description="Remove background from images using AI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return HTMLResponse(get_html())

@app.post("/api/remove-background")
async def remove_background(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        img = Image.open(io.BytesIO(contents))
        img_array = rembg.remove(img)
        output = io.BytesIO()
        Image.fromarray(img_array).save(output, format="PNG")
        output.seek(0)
        return FileResponse(
            io.BytesIO(output.getvalue()),
            media_type="image/png",
            filename="removed_bg.png"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/health")
async def health():
    return {"status": "healthy"}

def get_html():
    return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>BG Remover - Remove Image Backgrounds</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; }
        .container { background: white; border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); max-width: 600px; width: 100%; padding: 40px; }
        h1 { color: #333; margin-bottom: 10px; font-size: 2.5em; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .subtitle { color: #666; margin-bottom: 30px; font-size: 1.1em; }
        .upload-area { border: 3px dashed #667eea; border-radius: 15px; padding: 40px; text-align: center; cursor: pointer; background: #f8f9ff; margin-bottom: 20px; }
        .upload-area:hover { border-color: #764ba2; background: #f0f1ff; transform: scale(1.02); }
        .upload-icon { font-size: 3em; margin-bottom: 10px; }
        input[type="file"] { display: none; }
        button { flex: 1; padding: 12px 24px; border: none; border-radius: 10px; font-size: 1em; font-weight: 600; cursor: pointer; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4); }
        .btn-group { display: flex; gap: 10px; margin-top: 20px; }
        .preview-container { margin-top: 30px; display: none; }
        .preview-container.show { display: block; }
        .image-row { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .image-box { text-align: center; }
        .image-box img { max-width: 100%; border-radius: 10px; }
        .loading { display: none; text-align: center; padding: 20px; }
        .spinner { border: 4px solid #f3f3f3; border-top: 4px solid #667eea; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .error { color: #e74c3c; padding: 15px; background: #fadbd8; border-radius: 10px; display: none; margin-top: 20px; }
        .download-btn { background: linear-gradient(135deg, #2ecc71, #27ae60); color: white; padding: 12px 24px; border-radius: 10px; text-decoration: none; font-weight: 600; display: inline-block; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>✨ BG Remover</h1>
        <p class="subtitle">Remove image backgrounds instantly with AI</p>
        <div class="upload-area" id="uploadArea">
            <div class="upload-icon">📷</div>
            <div class="upload-text" style="color: #667eea; font-size: 1.2em; font-weight: 600; margin-bottom: 5px;">Click or drag your image</div>
            <div style="color: #999;">Supports JPG, PNG, WebP</div>
            <input type="file" id="fileInput" accept="image/*" />
        </div>
        <div class="btn-group">
            <button class="btn-primary" onclick="document.getElementById('fileInput').click()">Choose Image</button>
            <button style="background: #f0f0f0; color: #333;" onclick="resetForm()">Reset</button>
        </div>
        <div class="loading" id="loading"><div class="spinner"></div><p>Processing...</p></div>
        <div class="error" id="error"></div>
        <div class="preview-container" id="previewContainer">
            <div class="image-row">
                <div class="image-box"><h3>Original</h3><img id="originalImage" src="" /></div>
                <div class="image-box"><h3>No Background</h3><img id="resultImage" src="" /></div>
            </div>
            <div style="text-align: center;"><a href="#" id="downloadBtn" class="download-btn" download="removed_bg.png">⬇️ Download</a></div>
        </div>
    </div>
    <script>
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const loading = document.getElementById('loading');
        const error = document.getElementById('error');
        const previewContainer = document.getElementById('previewContainer');
        uploadArea.addEventListener('dragover', (e) => { e.preventDefault(); uploadArea.style.opacity = '0.7'; });
        uploadArea.addEventListener('dragleave', () => { uploadArea.style.opacity = '1'; });
        uploadArea.addEventListener('drop', (e) => { e.preventDefault(); uploadArea.style.opacity = '1'; fileInput.files = e.dataTransfer.files; processImage(); });
        fileInput.addEventListener('change', processImage);
        async function processImage() {
            const file = fileInput.files[0];
            if (!file) return;
            loading.classList.add('show');
            error.classList.remove('show');
            const reader = new FileReader();
            reader.onload = (e) => { document.getElementById('originalImage').src = e.target.result; };
            reader.readAsDataURL(file);
            try {
                const formData = new FormData();
                formData.append('file', file);
                const response = await fetch('/api/remove-background', { method: 'POST', body: formData });
                if (!response.ok) throw new Error('Processing failed');
                const blob = await response.blob();
                const objectUrl = URL.createObjectURL(blob);
                document.getElementById('resultImage').src = objectUrl;
                document.getElementById('downloadBtn').href = objectUrl;
                loading.classList.remove('show');
                previewContainer.classList.add('show');
            } catch (err) {
                loading.classList.remove('show');
                error.textContent = err.message;
                error.classList.add('show');
            }
        }
        function resetForm() { fileInput.value = ''; previewContainer.classList.remove('show'); error.classList.remove('show'); }
    </script>
</body>
</html>
    """
