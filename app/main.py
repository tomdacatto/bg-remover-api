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
    html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>BG Remover - Remove Image Backgrounds</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: "Segoe UI", sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; position: relative; overflow: hidden; }
        
        .sparkle { position: fixed; pointer-events: none; font-size: 2em; animation: sparkle-anim 2s ease-out forwards; }
        @keyframes sparkle-anim { 0% { opacity: 1; transform: translate(0, 0) scale(1); } 100% { opacity: 0; transform: translate(var(--tx), var(--ty)) scale(0); } }
        
        .container { background: white; border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); max-width: 700px; width: 100%; padding: 40px; z-index: 10; position: relative; }
        h1 { color: #333; margin-bottom: 10px; font-size: 2.5em; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .subtitle { color: #666; margin-bottom: 30px; font-size: 1.1em; }
        .upload-area { border: 3px dashed #667eea; border-radius: 15px; padding: 40px; text-align: center; cursor: pointer; background: #f8f9ff; margin-bottom: 20px; transition: all 0.3s; }
        .upload-area:hover { border-color: #764ba2; background: #f0f1ff; transform: scale(1.02); }
        .upload-area.drag { border-color: #764ba2; background: #e8ebff; }
        .upload-icon { font-size: 3em; margin-bottom: 10px; }
        input[type="file"] { display: none; }
        button { padding: 12px 24px; border: none; border-radius: 10px; font-size: 1em; font-weight: 600; cursor: pointer; transition: all 0.3s; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; flex: 1; }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4); }
        .btn-secondary { background: #f0f0f0; color: #333; flex: 1; margin-left: 10px; }
        .btn-secondary:hover { background: #e0e0e0; }
        .btn-group { display: flex; gap: 10px; margin-top: 20px; }
        
        .progress-container { display: none; margin: 20px 0; }
        .progress-container.show { display: block; }
        .progress-label { color: #666; font-size: 0.9em; margin-bottom: 8px; font-weight: 600; }
        .progress-bar { width: 100%; height: 8px; background: #e0e0e0; border-radius: 10px; overflow: hidden; }
        .progress-fill { height: 100%; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); width: 0%; transition: width 0.3s; border-radius: 10px; }
        
        .image-row { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
        .image-box { text-align: center; }
        .image-box h3 { color: #333; margin-bottom: 10px; font-size: 1.1em; }
        .image-box img { max-width: 100%; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
        .preview-container { margin-top: 30px; display: none; }
        .preview-container.show { display: block; animation: slideIn 0.5s ease-out; }
        @keyframes slideIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        
        .loading { display: none; text-align: center; padding: 20px; }
        .loading.show { display: block; }
        .spinner { border: 4px solid #f3f3f3; border-top: 4px solid #667eea; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto 10px; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        
        .error { color: #e74c3c; padding: 15px; background: #fadbd8; border-radius: 10px; display: none; margin-top: 20px; }
        .error.show { display: block; animation: shake 0.3s; }
        @keyframes shake { 0%, 100% { transform: translateX(0); } 25% { transform: translateX(-5px); } 75% { transform: translateX(5px); } }
        
        .download-btn { background: linear-gradient(135deg, #2ecc71, #27ae60); color: white; padding: 12px 24px; border-radius: 10px; text-decoration: none; font-weight: 600; display: inline-block; margin-top: 10px; transition: all 0.3s; border: none; cursor: pointer; }
        .download-btn:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(46, 204, 113, 0.4); }
    </style>
</head>
<body>
    <div class="container">
        <h1>✨ BG Remover</h1>
        <p class="subtitle">Remove image backgrounds instantly with AI</p>
        
        <div class="upload-area" id="uploadArea">
            <div class="upload-icon">📷</div>
            <div style="color: #667eea; font-size: 1.1em; font-weight: 600; margin-bottom: 5px;">Click or drag your image</div>
            <div style="color: #999;">Supports JPG, PNG, WebP</div>
            <input type="file" id="fileInput" accept="image/*" />
        </div>
        
        <div class="btn-group">
            <button class="btn-primary" onclick="document.getElementById('fileInput').click()">Choose Image</button>
            <button class="btn-secondary" onclick="resetForm()">Reset</button>
        </div>
        
        <div class="progress-container" id="progressContainer">
            <div class="progress-label">Processing your image...</div>
            <div class="progress-bar"><div class="progress-fill" id="progressFill"></div></div>
        </div>
        
        <div class="loading" id="loading"><div class="spinner"></div><p>Removing background...</p></div>
        
        <div class="error" id="error"></div>
        
        <div class="preview-container" id="previewContainer">
            <div class="image-row">
                <div class="image-box">
                    <h3>Original</h3>
                    <img id="originalImage" src="" alt="Original image" />
                </div>
                <div class="image-box">
                    <h3>✨ No Background</h3>
                    <img id="resultImage" src="" alt="Result image" />
                </div>
            </div>
            <div style="text-align: center;">
                <button class="download-btn" id="downloadBtn">⬇️ Download Result</button>
            </div>
        </div>
    </div>
    
    <script>
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const loading = document.getElementById('loading');
        const error = document.getElementById('error');
        const previewContainer = document.getElementById('previewContainer');
        const progressContainer = document.getElementById('progressContainer');
        const progressFill = document.getElementById('progressFill');
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('drag');
        });
        uploadArea.addEventListener('dragleave', () => uploadArea.classList.remove('drag'));
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drag');
            fileInput.files = e.dataTransfer.files;
            processImage();
        });
        fileInput.addEventListener('change', processImage);
        
        function createSparkles() {
            for (let i = 0; i < 5; i++) {
                const sparkle = document.createElement('div');
                sparkle.className = 'sparkle';
                sparkle.textContent = '✨';
                const angle = (Math.PI * 2 * i) / 5;
                const velocity = 100;
                const tx = Math.cos(angle) * velocity;
                const ty = Math.sin(angle) * velocity;
                sparkle.style.setProperty('--tx', tx + 'px');
                sparkle.style.setProperty('--ty', ty + 'px');
                sparkle.style.left = window.innerWidth / 2 + 'px';
                sparkle.style.top = window.innerHeight / 2 + 'px';
                document.body.appendChild(sparkle);
                setTimeout(() => sparkle.remove(), 2000);
            }
        }
        
        async function processImage() {
            const file = fileInput.files[0];
            if (!file) return;
            
            loading.classList.add('show');
            progressContainer.classList.add('show');
            error.classList.remove('show');
            previewContainer.classList.remove('show');
            progressFill.style.width = '10%';
            
            const reader = new FileReader();
            reader.onload = (e) => {
                document.getElementById('originalImage').src = e.target.result;
            };
            reader.readAsDataURL(file);
            
            try {
                const formData = new FormData();
                formData.append('file', file);
                
                setTimeout(() => { progressFill.style.width = '30%'; }, 300);
                
                const response = await fetch('/api/remove-background', {
                    method: 'POST',
                    body: formData
                });
                
                setTimeout(() => { progressFill.style.width = '70%'; }, 1000);
                
                if (!response.ok) throw new Error('Processing failed');
                
                const blob = await response.blob();
                const objectUrl = URL.createObjectURL(blob);
                
                document.getElementById('resultImage').src = objectUrl;
                document.getElementById('downloadBtn').onclick = () => {
                    const link = document.createElement('a');
                    link.href = objectUrl;
                    link.download = 'removed_bg.png';
                    link.click();
                };
                
                progressFill.style.width = '100%';
                setTimeout(() => {
                    loading.classList.remove('show');
                    progressContainer.classList.remove('show');
                    previewContainer.classList.add('show');
                    createSparkles();
                }, 500);
            } catch (err) {
                loading.classList.remove('show');
                progressContainer.classList.remove('show');
                error.textContent = 'Error: ' + err.message;
                error.classList.add('show');
            }
        }
        
        function resetForm() {
            fileInput.value = '';
            previewContainer.classList.remove('show');
            error.classList.remove('show');
            loading.classList.remove('show');
            progressContainer.classList.remove('show');
        }
    </script>
</body>
</html>
'''
    return html
