/** @odoo-module **/

// ==========================================================
//                       CONSTANTES
// ==========================================================
const multimediaContainer = document.getElementById('multimedia-container');
const addMultimediaBtn = document.getElementById('add-multimedia-btn');
const MAX_FIELDS = 3;

const mainImageInput = document.getElementById('main_image');
const mainImagePreviewContainer = mainImageInput ? mainImageInput.closest('.card').querySelector('.real-time-preview') : null;
const mainImageAlert = document.getElementById('main-image-alert');
const deleteMainImageBtn = mainImageInput ? mainImageInput.closest('.card').querySelector('.delete-image-btn') : null;
const mainImageInputContainer = mainImageInput ? mainImageInput.closest('.mt-3') : null;

const blogEntryHtmlInput = document.getElementById('blog_entry_html');
const blogEntryHtmlPreviewContainer = blogEntryHtmlInput ? blogEntryHtmlInput.closest('.card').querySelector('.real-time-preview') : null;
const blogEntryHtmlAlert = document.getElementById('blog-entry-html-alert');
const deleteBlogEntryHtmlBtn = blogEntryHtmlInput ? blogEntryHtmlInput.closest('.card').querySelector('.delete-image-btn') : null;
const blogEntryHtmlInputContainer = blogEntryHtmlInput ? blogEntryHtmlInput.closest('.mt-3') : null;


// ==========================================================
//                       FUNCIONES DE AYUDA
// ==========================================================

// Función principal para validar y previsualizar una imagen
function handleImageValidationAndPreview(fileInput, previewContainer, alertContainer, inputContainer, deleteBtn, options = {}) {
    const file = fileInput.files[0];
    const MAX_SIZE_MB = options.maxSizeMB || 2;
    const MIN_WIDTH = options.minWidth || 0;
    const MIN_HEIGHT = options.minHeight || 0;
    const MAX_WIDTH = options.maxWidth || Infinity;
    const MAX_HEIGHT = options.maxHeight || Infinity;

    const showAlert = (message) => {
        if (alertContainer) {
            alertContainer.textContent = message;
            alertContainer.classList.remove('d-none');
            alertContainer.classList.add('d-block');
        }
    };

    const hideAlert = () => {
        if (alertContainer) {
            alertContainer.classList.remove('d-block');
            alertContainer.classList.add('d-none');
        }
    };

    hideAlert();
    previewContainer.innerHTML = '<p class="text-muted">La previsualización aparecerá aquí.</p>';
    if (deleteBtn) {
        deleteBtn.style.display = 'none';
    }
    if (inputContainer) {
        inputContainer.classList.remove('d-none');
    }

    if (file) {
        if (file.size > MAX_SIZE_MB * 1024 * 1024) {
            showAlert(`¡Error! El tamaño del archivo debe ser menor a ${MAX_SIZE_MB} MB.`);
            fileInput.value = '';
            return;
        }

        const img = new Image();
        img.onload = () => {
            if (img.width < MIN_WIDTH || img.height < MIN_HEIGHT || img.width > MAX_WIDTH || img.height > MAX_HEIGHT) {
                const sizeError = (options.minWidth && options.minHeight && options.maxWidth && options.maxHeight)
                    ? `Las dimensiones de la imagen deben ser entre ${MIN_WIDTH}x${MIN_HEIGHT} px y ${MAX_WIDTH}x${MAX_HEIGHT} px.`
                    : (options.minWidth && options.minHeight)
                    ? `Las dimensiones de la imagen deben ser al menos ${MIN_WIDTH}x${MIN_HEIGHT} px.`
                    : `Las dimensiones de la imagen no deben exceder ${MAX_WIDTH}x${MAX_HEIGHT} px.`;
                showAlert(`¡Error! ${sizeError}`);
                fileInput.value = '';
            } else {
                previewContainer.innerHTML = `<img src="${img.src}" alt="Previsualización de imagen" class="img-fluid rounded shadow-sm" style="max-height: 400px; max-width: 550px;" />`;
                if (deleteBtn) {
                    deleteBtn.style.display = 'block';
                }
                if (inputContainer) {
                    inputContainer.classList.add('d-none');
                }
            }
        };
        img.src = URL.createObjectURL(file);
    }
}

// ... (Resto de tus funciones de ayuda: updateFieldIndices, checkMultimediaLimit, renderPreview) ...
function updateFieldIndices() {
    const blocks = multimediaContainer.querySelectorAll('.multimedia-block');
    blocks.forEach((block, index) => {
        block.querySelectorAll('[name]').forEach(input => {
            const name = input.getAttribute('name');
        });
    });
    checkMultimediaLimit();
}

function checkMultimediaLimit() {
    const currentFields = multimediaContainer.querySelectorAll('.multimedia-block').length;
    if (currentFields >= MAX_FIELDS) {
        addMultimediaBtn.style.display = 'none';
    } else {
        addMultimediaBtn.style.display = 'inline-block';
    }
}

function renderPreview(block, file, url) {
    const previewArea = block.querySelector('.real-time-preview');
    previewArea.innerHTML = '';
    if (file) {
        const fileType = file.type;
        if (fileType.startsWith('image/')) {
            const img = document.createElement('img');
            img.src = URL.createObjectURL(file);
            img.className = 'img-fluid rounded shadow-sm';
            previewArea.appendChild(img);
        } else if (fileType === 'application/pdf') {
            const embed = document.createElement('embed');
            embed.src = URL.createObjectURL(file);
            embed.type = 'application/pdf';
            embed.style.cssText = 'width: 100%; height: 60vh;';
            previewArea.appendChild(embed);
        } else if (fileType.startsWith('video/')) {
             const video = document.createElement('video');
             video.src = URL.createObjectURL(file);
             video.controls = true;
             video.className = 'w-100 rounded shadow-sm';
             previewArea.appendChild(video);
        }
    } else if (url) {
        if (url.includes('youtube.com') || url.includes('youtu.be')) {
            const videoId = url.split('v=')[1] || url.split('/').pop();
            const iframe = document.createElement('iframe');
            iframe.width = '560';
            iframe.height = '315';
            iframe.src = `https://www.youtube.com/embed/${videoId}`;
            iframe.setAttribute('frameborder', '0');
            iframe.setAttribute('allowfullscreen', 'allowfullscreen');
            iframe.setAttribute('allow', 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture');
            previewArea.appendChild(iframe);
        } else {
            const p = document.createElement('p');
            p.className = 'text-muted';
            p.textContent = 'Enlace de video no reconocido. Solo se admiten enlaces de YouTube.';
            previewArea.appendChild(p);
        }
    } else {
        const p = document.createElement('p');
        p.className = 'text-muted';
        p.textContent = 'La previsualización aparecerá aquí.';
        previewArea.appendChild(p);
    }
}


// ==========================================================
//                       MANEJADORES DE EVENTOS
// ==========================================================

// Eventos para el campo main_image
if (mainImageInput) {
    mainImageInput.addEventListener('change', () => {
        handleImageValidationAndPreview(mainImageInput, mainImagePreviewContainer, mainImageAlert, mainImageInputContainer, deleteMainImageBtn, {maxWidth: 1920, maxHeight: 1024});
    });
}
if (deleteMainImageBtn) {
    deleteMainImageBtn.addEventListener('click', (event) => {
        event.preventDefault();
        mainImageInput.value = '';
        mainImagePreviewContainer.innerHTML = '<p class="text-muted">La previsualización aparecerá aquí.</p>';
        mainImageInputContainer.classList.remove('d-none');
        deleteMainImageBtn.style.display = 'none';
    });
}

// Eventos para el campo blog_entry_html
if (blogEntryHtmlInput) {
    blogEntryHtmlInput.addEventListener('change', () => {
        handleImageValidationAndPreview(blogEntryHtmlInput, blogEntryHtmlPreviewContainer, blogEntryHtmlAlert, blogEntryHtmlInputContainer, deleteBlogEntryHtmlBtn, {minWidth: 1920, minHeight: 1080});
    });
}
if (deleteBlogEntryHtmlBtn) {
    deleteBlogEntryHtmlBtn.addEventListener('click', (event) => {
        event.preventDefault();
        blogEntryHtmlInput.value = '';
        blogEntryHtmlPreviewContainer.innerHTML = '<p class="text-muted">La previsualización aparecerá aquí.</p>';
        blogEntryHtmlInputContainer.classList.remove('d-none');
        deleteBlogEntryHtmlBtn.style.display = 'none';
    });
}

// Delegación de eventos para los cambios en los bloques multimedia
if (multimediaContainer) {
    multimediaContainer.addEventListener('change', (event) => {
        const target = event.target;
        const block = target.closest('.multimedia-block');
        const fileContainer = block.querySelector('.file-container');
        const urlContainer = block.querySelector('.url-container');
        const fileInput = block.querySelector('.content-file-input');
        const urlInput = block.querySelector('.content-url-input');

        if (target.classList.contains('content-type-select')) {
            const selectedType = target.value;
            fileContainer.style.display = (selectedType === 'image' || selectedType === 'file' || selectedType === 'videoMp4') ? 'block' : 'none';
            urlContainer.style.display = (selectedType === 'video') ? 'block' : 'none';

            let acceptValue = '';
            if (selectedType === 'image') {
                acceptValue = 'image/*';
            } else if (selectedType === 'file') {
                acceptValue = '.pdf, .docx, .xlsx, .pptx';
            } else if (selectedType === 'videoMp4') {
                acceptValue = 'video/mp4';
            }
            fileInput.setAttribute('accept', acceptValue);

            fileInput.value = '';
            urlInput.value = '';
            renderPreview(block, null, null);
        }

        if (target.classList.contains('content-file-input') && target.offsetParent !== null) {
            const file = target.files[0];
            if (file) {
                renderPreview(block, file, null);
            }
        }
    });

    multimediaContainer.addEventListener('input', (event) => {
        const target = event.target;
        if (target.classList.contains('content-url-input') && target.offsetParent !== null) {
            const block = target.closest('.multimedia-block');
            const url = target.value;
            renderPreview(block, null, url);
        }
    });

    multimediaContainer.addEventListener('click', (event) => {
        const target = event.target;
        if (target.closest('.delete-multimedia-btn')) {
            const block = target.closest('.multimedia-block');
            block.remove();
            updateFieldIndices();
        }
    });

    addMultimediaBtn.addEventListener('click', () => {
        const currentFields = multimediaContainer.querySelectorAll('.multimedia-block').length;
        if (currentFields < MAX_FIELDS) {
            const newIndex = multimediaContainer.querySelectorAll('.multimedia-block').length * -1;
            const newBlock = document.createElement('div');
            newBlock.className = 'multimedia-block row mb-5 align-items-center bg-white g-0 border rounded position-relative p-3 shadow-sm';
            newBlock.innerHTML = `
                <button type="button" class="btn w-auto btn-sm position-absolute top-0 end-0 m-2 delete-multimedia-btn" style="z-index: 10;">
                    <i class="fa fa-trash"></i>
                </button>
                <input type="hidden" name="multimedia_ids[${newIndex}].id" value="0"/>
                <div class="col-md-4 p-3">
                    <label class="form-label mb-2 fw-bold">Tipo de Contenido</label>
                    <select name="multimedia_ids[${newIndex}].content_type" class="form-select w-100 content-type-select">
                        <option value="none" selected="selected">Ninguno</option>
                        <option value="image">Imagen</option>
                        <option value="file">Archivo (PDF, DOCX, XLSX, PPTX)</option>
                        <option value="videoMp4">Video (video/mp4)</option>
                        <option value="video">Video (Enlace URL)</option>
                    </select>
                </div>
                <div class="col-md-8 p-3">
                    <div class="file-container mb-3" style="display: none;">
                        <label class="form-label">Sube tu archivo</label>
                        <input type="file" name="multimedia_ids[${newIndex}].content_file" class="form-control content-file-input"/>
                        <small class="form-text text-muted">Archivos permitidos: Imagen, Video, Documento.</small>
                        <input type="hidden"
                               name="multimedia_ids[${newIndex}].content_file_filename"/>
                        <input type="hidden"
                               name="multimedia_ids[${newIndex}].content_file_mimetype"/>
                    </div>
                    <div class="url-container mb-3" style="display: none;">
                        <label class="form-label">Pega el enlace del video</label>
                        <input type="url" name="multimedia_ids[${newIndex}].content_url" class="form-control content-url-input"/>
                    </div>
                    <div class="real-time-preview mt-3 p-3 bg-light rounded text-center">
                        <p class="text-muted">La previsualización aparecerá aquí.</p>
                    </div>
                </div>
            `;
            multimediaContainer.appendChild(newBlock);
            checkMultimediaLimit();
        }
    });
}


// ==========================================================
//                       INICIALIZACIÓN
// ==========================================================

if (multimediaContainer) {
    updateFieldIndices();

    multimediaContainer.querySelectorAll('.multimedia-block').forEach(block => {
        const select = block.querySelector('.content-type-select');
        const fileInput = block.querySelector('.content-file-input');
        const selectedType = select.value;

        if (select) {
            let acceptValue = '';
            if (selectedType === 'image') {
                acceptValue = 'image/*';
            } else if (selectedType === 'file') {
                acceptValue = '.pdf, .docx, .xlsx, .pptx';
            } else if (selectedType === 'videoMp4') {
                acceptValue = 'video/mp4';
            }
            if (fileInput) {
                 fileInput.setAttribute('accept', acceptValue);
            }
        }
    });
}