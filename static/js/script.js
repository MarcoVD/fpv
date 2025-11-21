// Variable para guardar la única instancia del modal PDF. Esto evita el error de re-inicialización.
let pdfModalInstance = null; 

// Función para inicializar y obtener la instancia de Bootstrap Modal (solo una vez)
const getPDFModal = () => {
    if (!pdfModalInstance) {
        const modalElement = document.getElementById('ModalPDF');
        if (modalElement) {
            // Inicialización de la instancia de Bootstrap Modal
            pdfModalInstance = new bootstrap.Modal(modalElement);
        }
    }
    return pdfModalInstance;
};

// 1. Contenido para la Documentación (Listas)
const contenidoDocumentacion = {
    'pfisica': {
        title: 'Documentación para Personas físicas',
        items: [
            '1. Identificación oficial vigente con fotografía y firma.',
            '2. CURP actualizado del solicitante.',
            '3. RFC actualizado del solicitante.',
            '4. Comprobante de domicilio reciente.',
            '5. Título de concesión vigente o documento que acredite la posesión legal de la concesión.',
            '6. Documento que acredite la propiedad del vehículo, como factura, carta factura.',
            '7. Solicitud de inscripción al programa, con datos personales y de contacto.',
            '8. Carta compromiso y aviso de privacidad firmados.'
        ]
    },
    'pmorales': {
        title: 'Documentación Adicional para Personas morales',
        items: [
            '1. Acta constitutiva debidamente protocolizada ante fedatario público.',
            '2. Poder notarial vigente que acredite al representante legal con facultades para actos de administración.',
            '3. Identificación oficial vigente del representante legal.',
            '4. RFC de la persona moral.',
            '5. Comprobante de domicilio fiscal reciente.',
            '6. Acta de asamblea protocolizada, en caso de existir reformas o cambios recientes.',
            '7. Opinión positiva de cumplimiento fiscal, emitida por el Servicio de Administración Tributaria (SAT).'
        ]
    },
    'vehiculo': {
        title: 'Documentación Del vehículo',
        items: [
            '1. Factura a nombre del sucesorio o debidamente endosada, o documento que acredite robo o extravío.',
            '2. Tarjeta de circulación vigente o permiso provisional.',
            '3. Comprobantes de pago de tenencia y derechos del ejercicio fiscal 2025.',
            '4. Fotografías del vehículo, placa y número de identificación vehicular.',
            '5. Póliza de seguro vigente, con cobertura para pasajeros.'
        ]
    }
};

// Nuevo: Contenido para los PDFs (Enlaces y títulos)
const contenidoPDFs = {
    'convocatoria': {
        title: 'Convocatoria y Reglas de Operación',
        path: '/static/pdf/convocatoria.pdf' // ruta 
    },
    'catalogo': {
        title: 'Catálogo de autos',
        path: '/static/pdf/catalogos_autos.pdf' // ruta 
    },
    'solicitud': {
        title: 'Solicitud',
        path: '/static/pdf/solicitud.pdf' // ruta 
    },
    'carta': {
        title: 'Carta compromiso',
        path: '/static/pdf/CARTA_COMPROMISO.pdf' // ruta 
    },
    // Añadido el objeto para el aviso de privacidad
    'aviso_privacidad': { 
        title: 'Aviso de Privacidad',
        path: '/static/pdf/Aviso_de_Privacidad.pdf' // La ruta debe coincidir con la de tu archivo
    }
};

// Función para actualizar el modal de Documentación (Listas)
const updateDocModalContent = (type) => {
    const data = contenidoDocumentacion[type];
    if (!data) return;

    const modalTitle = document.getElementById('modalDocumentacionTitle');
    const modalBody = document.getElementById('modalDocumentacionBody');

    // Limpiar contenido anterior
    modalBody.innerHTML = '';

    // Asignar nuevo título
    modalTitle.textContent = data.title;

    // Crear y añadir nuevos elementos de la lista
    const ul = document.createElement('ul');
    ul.className = 'list-group';
    data.items.forEach(itemText => {
        const listItem = document.createElement('li');
        listItem.className = 'list-group-item';
        listItem.textContent = itemText;
        ul.appendChild(listItem);
    });
    modalBody.appendChild(ul);

    // Abrir el modal
    const myModal = new bootstrap.Modal(document.getElementById('ModalDocumentacion'));
    myModal.show();
};

// Nueva función para actualizar el modal de PDF (Embeds)
const updatePDFModalContent = (type) => {
    const data = contenidoPDFs[type];
    if (!data) return;

    const modalTitle = document.getElementById('modalPDFTitle');
    const modalBody = document.getElementById('modalPDFBody');

    // Limpiar contenido anterior
    modalBody.innerHTML = '';

    // Asignar nuevo título
    modalTitle.textContent = data.title;

    // Crear y añadir el embed del PDF
    const pdfEmbed = document.createElement('embed');
    pdfEmbed.src = data.path;
    pdfEmbed.type = 'application/pdf';
    pdfEmbed.width = '100%';
    pdfEmbed.height = '600px';
    modalBody.appendChild(pdfEmbed);

    // Abrir el modal usando la instancia única (CORRECCIÓN CLAVE)
    const myModal = getPDFModal();
    if (myModal) {
        myModal.show();
    }
};

// 2. Capturar eventos de clic
document.addEventListener('DOMContentLoaded', () => {
    // Eventos para la Documentación (Listas)
    const docLinks = document.querySelectorAll('.btn-doc-modal');

    docLinks.forEach(link => {
        link.addEventListener('click', (event) => {
            event.preventDefault();
            const type = link.getAttribute('data-modal-type');
            if (type) {
                updateDocModalContent(type);
            }
        });
    });

    // Eventos para los PDFs (Convocatoria, Solicitud, Carta y Aviso de Privacidad)
    const pdfLinks = document.querySelectorAll('.btn-pdf-modal');

    pdfLinks.forEach(link => {
        link.addEventListener('click', (event) => {
            event.preventDefault();
            const type = link.getAttribute('data-modal-type');
            if (type) {
                updatePDFModalContent(type);
            }
        });
    });
});