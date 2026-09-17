const API_URL = window.location.origin + "/api";
let seccionActual = 'dashboard';
let chartInstance = null;

document.addEventListener('DOMContentLoaded', () => {
    const user = JSON.parse(sessionStorage.getItem('user'));
    if (!user) { window.location.href = 'login.html'; return; }

    document.getElementById('user-display-name').innerText = user.nombre;
    const rolesMap = { 1: 'ADMINISTRADOR', 2: 'OPERATIVO', 3: 'DOCENTE' };
    document.getElementById('user-display-role').innerText = rolesMap[user.id_rol];

    // --- TRANSFORMACIÓN DE INTERFAZ (RBAC) ---
    const rol = parseInt(user.id_rol);
    if (rol === 3) { // DOCENTE: No ve Docentes, Reservas Globales ni Roles
        ['nav-docentes', 'nav-reservas', 'nav-roles'].forEach(id => {
            const el = document.getElementById(id); if(el) el.style.display = 'none';
        });
        document.getElementById('seccion-grafico').style.display = 'none';
    } else if (rol === 2) { // OPERATIVO: No ve Control de Roles
        const el = document.getElementById('nav-roles'); if(el) el.style.display = 'none';
    }

    mostrarSeccion('dashboard');
});

async function mostrarSeccion(seccion) {
    seccionActual = seccion;
    const user = JSON.parse(sessionStorage.getItem('user'));
    const btn = document.getElementById('btn-accion-principal');
    const tit = document.getElementById('titulo-seccion');

    document.querySelectorAll('.sidebar-item').forEach(el => el.classList.remove('sidebar-active'));
    
    // Asignar sidebar active según corresponda
    let sideId = 'nav-' + seccion.split('_')[0];
    document.getElementById(sideId)?.classList.add('sidebar-active');

    btn.style.display = 'flex';
    
    if (seccion === 'dashboard') {
        tit.innerText = user.id_rol == 3 ? "Mis Reservas" : "Dashboard General";
        btn.innerHTML = '<i class="fas fa-plus"></i> NUEVA RESERVA';
        btn.onclick = () => prepararModal('reserva');
        await cargarTabla('reservas');
        initChart();
    } else if (seccion === 'salones') {
        tit.innerText = "Gestión de Salones";
        btn.innerHTML = '<i class="fas fa-plus"></i> REGISTRAR SALÓN';
        btn.onclick = () => prepararModal('salon');
        if (user.id_rol != 1) btn.style.display = 'none'; // US-05: Solo admin puede registrar
        await cargarTabla('salones');
    } else if (seccion === 'reservas_globales') {
        tit.innerText = "Reservas Globales";
        btn.style.display = 'none'; // No se crean desde este panel global
        await cargarTabla('reservas_globales');
    } else if (seccion === 'docentes') {
        tit.innerText = "Listado de Docentes";
        btn.innerHTML = '<i class="fas fa-plus"></i> REGISTRAR DOCENTE';
        btn.onclick = () => prepararModal('docente');
        if (user.id_rol != 1) btn.style.display = 'none'; // US-13: Solo admin
        await cargarTabla('docentes');
    } else if (seccion === 'roles') {
        tit.innerText = "Control de Roles";
        btn.style.display = 'none';
        await cargarTabla('roles');
    }
}

async function cargarTabla(tipo) {
    const user = JSON.parse(sessionStorage.getItem('user'));
    const head = document.getElementById('tabla-head');
    const body = document.getElementById('tabla-body');
    body.innerHTML = "<tr><td colspan='5' class='p-10 text-center text-slate-400 italic'>Sincronizando con Supabase...</td></tr>";

    try {
        let fetchUrl = `${API_URL}/${tipo}`;
        if (tipo === 'reservas_globales') {
            fetchUrl = `${API_URL}/reservas`;
        }
        
        const res = await fetch(fetchUrl);
        const result = await res.json();
        body.innerHTML = "";

        if (tipo === 'reservas' || tipo === 'reservas_globales') {
            head.innerHTML = '<tr><th class="px-6 py-4">Docente</th><th class="px-6 py-4">Salón</th><th class="px-6 py-4">Fecha</th><th class="px-6 py-4">Horario</th><th class="px-6 py-4">Acción</th></tr>';
            
            let data = result.data || [];
            // Si es vista del docente, filtrar únicamente sus reservas
            if (tipo === 'reservas' && user.id_rol == 3) {
                data = data.filter(r => r.id_docente == user.id_usuario);
            }

            if (data.length === 0) {
                body.innerHTML = "<tr><td colspan='5' class='p-10 text-center text-slate-400 italic'>No hay reservas registradas</td></tr>";
            } else {
                data.forEach(r => {
                    const h_ini = r.hora_inicio ? r.hora_inicio.substring(0,5) : '--:--';
                    const h_fin = r.hora_fin ? r.hora_fin.substring(0,5) : '--:--';
                    
                    // Botón editar condicional (Administrador o Administrativo)
                    const canEdit = user.id_rol == 1 || user.id_rol == 2;
                    const btnEditar = canEdit ? `<button onclick="editarReserva(${r.id_reserva}, '${r.fecha}', '${h_ini}', '${h_fin}', ${r.id_salon}, ${r.id_docente})" class="text-blue-600 font-bold hover:underline mr-4"><i class="fas fa-edit"></i></button>` : '';

                    body.innerHTML += `
                        <tr class="border-b hover:bg-slate-50/50 transition">
                            <td class="px-6 py-4 font-bold text-slate-700">${r.docente}</td>
                            <td class="px-6 py-4 text-slate-600">${r.salon}</td>
                            <td class="px-6 py-4 text-slate-600">${r.fecha}</td>
                            <td class="px-6 py-4 text-slate-600"><span class="bg-blue-50 text-blue-700 px-2.5 py-1 rounded-lg text-xs font-bold">${h_ini} - ${h_fin}</span></td>
                            <td class="px-6 py-4">
                                ${btnEditar}
                                <button onclick="cancelarReserva(${r.id_reserva})" class="text-red-500 font-bold hover:underline"><i class="fas fa-trash-alt"></i> Cancelar</button>
                            </td>
                        </tr>`;
                });
            }
            if (tipo === 'reservas') {
                document.getElementById('stat-reservas').innerText = data.length;
            }
        } else if (tipo === 'salones') {
            head.innerHTML = '<tr><th class="px-6 py-4">Nombre</th><th class="px-6 py-4">Capacidad</th><th class="px-6 py-4">Ubicación</th><th class="px-6 py-4">Estado</th><th class="px-6 py-4">Acción</th></tr>';
            
            if (!result.data || result.data.length === 0) {
                body.innerHTML = "<tr><td colspan='5' class='p-10 text-center text-slate-400 italic'>No hay salones registrados</td></tr>";
            } else {
                result.data.forEach(s => {
                    const badgeColor = s.estado === 'disponible' ? 'bg-green-50 text-green-700' : 'bg-amber-50 text-amber-700';
                    body.innerHTML += `
                        <tr class="border-b hover:bg-slate-50/50 transition">
                            <td class="px-6 py-4 font-bold text-slate-700">${s.nombre}</td>
                            <td class="px-6 py-4 text-slate-600">${s.capacidad} personas</td>
                            <td class="px-6 py-4 text-slate-600">${s.ubicacion}</td>
                            <td class="px-6 py-4"><span class="${badgeColor} px-2.5 py-1 rounded-lg text-xs font-bold uppercase">${s.estado}</span></td>
                            <td class="px-6 py-4">${user.id_rol == 1 ? `<button onclick="editarSalon(${s.id_salon}, '${s.nombre}', ${s.capacidad}, '${s.ubicacion}')" class="text-blue-600 font-bold hover:underline"><i class="fas fa-edit"></i> Editar</button>` : '-'}</td>
                        </tr>`;
                });
            }
        } else if (tipo === 'docentes') {
            head.innerHTML = '<tr><th class="px-6 py-4">ID Docente</th><th class="px-6 py-4">Nombre</th><th class="px-6 py-4">Correo</th><th class="px-6 py-4">Perfil</th></tr>';
            
            const dataList = result.data || [];
            if (dataList.length === 0) {
                body.innerHTML = "<tr><td colspan='4' class='p-10 text-center text-slate-400 italic'>No hay docentes registrados</td></tr>";
            } else {
                dataList.forEach(d => {
                    body.innerHTML += `
                        <tr class="border-b hover:bg-slate-50/50 transition">
                            <td class="px-6 py-4 text-slate-500 font-mono">#${d.id_docente}</td>
                            <td class="px-6 py-4 font-bold text-slate-700">${d.nombre}</td>
                            <td class="px-6 py-4 text-slate-600">${d.correo}</td>
                            <td class="px-6 py-4"><span class="bg-purple-50 text-purple-700 px-2.5 py-1 rounded-lg text-xs font-bold uppercase">Docente</span></td>
                        </tr>`;
                });
            }
        } else if (tipo === 'roles') {
            head.innerHTML = '<tr><th class="px-6 py-4">ID Rol</th><th class="px-6 py-4">Nombre del Rol</th><th class="px-6 py-4">Estatus</th></tr>';
            
            const dataList = result || [];
            if (dataList.length === 0) {
                body.innerHTML = "<tr><td colspan='3' class='p-10 text-center text-slate-400 italic'>No hay roles configurados</td></tr>";
            } else {
                dataList.forEach(r => {
                    body.innerHTML += `
                        <tr class="border-b hover:bg-slate-50/50 transition">
                            <td class="px-6 py-4 text-slate-500 font-mono">#${r.id_rol}</td>
                            <td class="px-6 py-4 font-bold text-slate-700">${r.nombre}</td>
                            <td class="px-6 py-4 text-green-600"><span class="flex items-center gap-1.5"><span class="w-1.5 h-1.5 bg-green-500 rounded-full"></span> Activo</span></td>
                        </tr>`;
                });
            }
        }
    } catch (e) { 
        body.innerHTML = "<tr><td colspan='5' class='p-10 text-center text-red-500 font-bold'>Error de red al conectar con el servidor</td></tr>"; 
    }
}

function prepararModal(tipo, editData = null) {
    const user = JSON.parse(sessionStorage.getItem('user'));
    const campos = document.getElementById('campos-dinamicos');
    campos.innerHTML = "";

    if (tipo === 'reserva') {
        document.getElementById('modal-titulo').innerText = editData ? "Editar Reserva" : "Nueva Reserva";
        campos.innerHTML = `
            ${editData ? `<input type="hidden" id="m-reserva-id" value="${editData.id_reserva}">` : ''}
            <div class="space-y-1">
                <label class="text-xs font-bold text-slate-400 uppercase">Fecha</label>
                <input type="date" id="m-fecha" class="w-full p-3 border border-slate-200 rounded-2xl outline-none focus:ring-2 focus:ring-blue-500 transition" required value="${editData ? editData.fecha : ''}">
            </div>
            <div class="grid grid-cols-2 gap-4">
                <div class="space-y-1">
                    <label class="text-xs font-bold text-slate-400 uppercase">Hora Inicio</label>
                    <input type="time" id="m-inicio" class="w-full p-3 border border-slate-200 rounded-2xl outline-none focus:ring-2 focus:ring-blue-500 transition" required value="${editData ? editData.hora_inicio : ''}">
                </div>
                <div class="space-y-1">
                    <label class="text-xs font-bold text-slate-400 uppercase">Hora Fin</label>
                    <input type="time" id="m-fin" class="w-full p-3 border border-slate-200 rounded-2xl outline-none focus:ring-2 focus:ring-blue-500 transition" required value="${editData ? editData.hora_fin : ''}">
                </div>
            </div>
            <div class="space-y-1">
                <label class="text-xs font-bold text-slate-400 uppercase">ID del Salón</label>
                <input type="number" id="m-salon" placeholder="ID del Salón" class="w-full p-3 border border-slate-200 rounded-2xl outline-none focus:ring-2 focus:ring-blue-500 transition" required value="${editData ? editData.id_salon : ''}">
            </div>
            ${user.id_rol != 3 ? `
            <div class="space-y-1">
                <label class="text-xs font-bold text-slate-400 uppercase">ID del Docente</label>
                <input type="number" id="m-docente" placeholder="ID del Docente" class="w-full p-3 border border-slate-200 rounded-2xl outline-none focus:ring-2 focus:ring-blue-500 transition" required value="${editData ? editData.id_docente : ''}">
            </div>
            ` : ''}
        `;
        document.getElementById('modalMaestro').classList.remove('hidden');
        document.getElementById('formMaestro').onsubmit = (e) => enviarFormulario(e, editData ? 'editar_reserva' : 'reserva');
    } else if (tipo === 'salon') {
        document.getElementById('modal-titulo').innerText = "Registrar Salón";
        campos.innerHTML = `
            <div class="space-y-1">
                <label class="text-xs font-bold text-slate-400 uppercase">Nombre</label>
                <input type="text" id="m-nom" placeholder="Ej: Laboratorio 402" class="w-full p-3 border border-slate-200 rounded-2xl outline-none focus:ring-2 focus:ring-blue-500 transition" required>
            </div>
            <div class="space-y-1">
                <label class="text-xs font-bold text-slate-400 uppercase">Capacidad</label>
                <input type="number" id="m-cap" placeholder="Ej: 40" class="w-full p-3 border border-slate-200 rounded-2xl outline-none focus:ring-2 focus:ring-blue-500 transition" required>
            </div>
            <div class="space-y-1">
                <label class="text-xs font-bold text-slate-400 uppercase">Ubicación</label>
                <input type="text" id="m-ub" placeholder="Ej: Torre B - Piso 4" class="w-full p-3 border border-slate-200 rounded-2xl outline-none focus:ring-2 focus:ring-blue-500 transition" required>
            </div>
        `;
        document.getElementById('modalMaestro').classList.remove('hidden');
        document.getElementById('formMaestro').onsubmit = (e) => enviarFormulario(e, 'salon');
    } else if (tipo === 'docente') {
        document.getElementById('modal-titulo').innerText = "Registrar Docente";
        campos.innerHTML = `
            <div class="space-y-1">
                <label class="text-xs font-bold text-slate-400 uppercase">Nombre Completo</label>
                <input type="text" id="m-nom-doc" placeholder="Ej: Ing. María Pérez" class="w-full p-3 border border-slate-200 rounded-2xl outline-none focus:ring-2 focus:ring-blue-500 transition" required>
            </div>
            <div class="space-y-1">
                <label class="text-xs font-bold text-slate-400 uppercase">Correo Institucional</label>
                <input type="email" id="m-corr-doc" placeholder="maria.perez@ucatolica.edu.co" class="w-full p-3 border border-slate-200 rounded-2xl outline-none focus:ring-2 focus:ring-blue-500 transition" required>
            </div>
        `;
        document.getElementById('modalMaestro').classList.remove('hidden');
        document.getElementById('formMaestro').onsubmit = (e) => enviarFormulario(e, 'docente');
    }
}

function editarSalon(id, nombre, capacidad, ubicacion) {
    const campos = document.getElementById('campos-dinamicos');
    document.getElementById('modal-titulo').innerText = "Editar Salón";
    campos.innerHTML = `
        <input type="hidden" id="m-id-edit" value="${id}">
        <div class="space-y-1">
            <label class="text-xs font-bold text-slate-400 uppercase">Nombre</label>
            <input type="text" id="m-nom-edit" class="w-full p-3 border border-slate-200 rounded-2xl outline-none focus:ring-2 focus:ring-blue-500 transition" value="${nombre}" required>
        </div>
        <div class="space-y-1">
            <label class="text-xs font-bold text-slate-400 uppercase">Capacidad</label>
            <input type="number" id="m-cap-edit" class="w-full p-3 border border-slate-200 rounded-2xl outline-none focus:ring-2 focus:ring-blue-500 transition" value="${capacidad}" required>
        </div>
        <div class="space-y-1">
            <label class="text-xs font-bold text-slate-400 uppercase">Ubicación</label>
            <input type="text" id="m-ub-edit" class="w-full p-3 border border-slate-200 rounded-2xl outline-none focus:ring-2 focus:ring-blue-500 transition" value="${ubicacion}" required>
        </div>
    `;
    document.getElementById('modalMaestro').classList.remove('hidden');
    document.getElementById('formMaestro').onsubmit = (e) => enviarFormulario(e, 'editar_salon');
}

function editarReserva(id_reserva, fecha, hora_inicio, hora_fin, id_salon, id_docente) {
    prepararModal('reserva', { id_reserva, fecha, hora_inicio, hora_fin, id_salon, id_docente });
}

async function enviarFormulario(e, tipo) {
    e.preventDefault();
    const user = JSON.parse(sessionStorage.getItem('user'));
    let data = {};
    let endpoint = `${API_URL}/${tipo}s`;
    let method = 'POST';
    
    if (tipo === 'reserva') {
        const id_docente_val = user.id_rol == 3 ? user.id_usuario : document.getElementById('m-docente').value;
        data = { 
            fecha: document.getElementById('m-fecha').value, 
            hora_inicio: document.getElementById('m-inicio').value, 
            hora_fin: document.getElementById('m-fin').value,
            id_salon: parseInt(document.getElementById('m-salon').value), 
            id_docente: parseInt(id_docente_val)
        };
    } else if (tipo === 'editar_reserva') {
        const id_reserva = document.getElementById('m-reserva-id').value;
        const id_docente_val = user.id_rol == 3 ? user.id_usuario : document.getElementById('m-docente').value;
        data = { 
            fecha: document.getElementById('m-fecha').value, 
            hora_inicio: document.getElementById('m-inicio').value, 
            hora_fin: document.getElementById('m-fin').value,
            id_salon: parseInt(document.getElementById('m-salon').value), 
            id_docente: parseInt(id_docente_val)
        };
        endpoint = `${API_URL}/reservas/${id_reserva}`;
        method = 'PUT';
    } else if (tipo === 'salon') {
        data = { 
            nombre: document.getElementById('m-nom').value, 
            capacidad: parseInt(document.getElementById('m-cap').value), 
            ubicacion: document.getElementById('m-ub').value 
        };
        endpoint = `${API_URL}/salones`;
    } else if (tipo === 'editar_salon') {
        const salonId = document.getElementById('m-id-edit').value;
        data = { 
            nombre: document.getElementById('m-nom-edit').value, 
            capacidad: parseInt(document.getElementById('m-cap-edit').value), 
            ubicacion: document.getElementById('m-ub-edit').value 
        };
        endpoint = `${API_URL}/salones/${salonId}`;
        method = 'PUT';
    } else if (tipo === 'docente') {
        data = {
            nombre: document.getElementById('m-nom-doc').value,
            correo: document.getElementById('m-corr-doc').value
        };
    }
    
    try {
        const res = await fetch(endpoint, { 
            method: method, 
            headers: {'Content-Type': 'application/json'}, 
            body: JSON.stringify(data) 
        });
        const result = await res.json();
        alert(result.message || "Operación realizada con éxito");
        cerrarModal();
        mostrarSeccion(seccionActual);
    } catch (err) {
        alert("Error al enviar el formulario.");
    }
}

async function cancelarReserva(id) {
    if (confirm("¿Estás seguro de que deseas cancelar esta reserva? (US-26 / US-29)")) {
        try {
            const res = await fetch(`${API_URL}/reservas/${id}`, {
                method: 'DELETE'
            });
            const result = await res.json();
            if (res.ok) {
                alert("Reserva cancelada correctamente");
                mostrarSeccion(seccionActual);
            } else {
                alert("Error: " + result.message);
            }
        } catch (e) {
            alert("Error de conexión al intentar cancelar la reserva");
        }
    }
}

function cerrarModal() { document.getElementById('modalMaestro').classList.add('hidden'); }
function cerrarSesion() { sessionStorage.clear(); window.location.href = 'login.html'; }
function recargarSeccionActual() { mostrarSeccion(seccionActual); }

async function initChart() {
    const user = JSON.parse(sessionStorage.getItem('user'));
    if (user.id_rol == 3) return; // Docente no tiene permisos del gráfico

    try {
        const res = await fetch(`${API_URL}/reservas`);
        const result = await res.json();
        if (!res.ok || !result.data) return;

        // Agrupar reservas por salón
        const salonesMap = {};
        result.data.forEach(r => {
            if (r.estado !== 'cancelada') {
                salonesMap[r.salon] = (salonesMap[r.salon] || 0) + 1;
            }
        });

        const labels = Object.keys(salonesMap);
        const data = Object.values(salonesMap);

        const canvas = document.getElementById('reservasChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (chartInstance) {
            chartInstance.destroy();
        }

        chartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Reservas Activas por Salón',
                    data: data,
                    backgroundColor: 'rgba(37, 99, 235, 0.65)',
                    borderColor: 'rgba(37, 99, 235, 1)',
                    borderWidth: 2,
                    borderRadius: 12,
                    barPercentage: 0.5,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#1e293b',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        padding: 12,
                        cornerRadius: 8,
                    }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { color: '#94a3b8', font: { weight: 'bold' } }
                    },
                    y: {
                        beginAtZero: true,
                        grid: { color: '#f1f5f9' },
                        ticks: { 
                            color: '#94a3b8', 
                            stepSize: 1,
                            font: { weight: 'bold' }
                        }
                    }
                }
            }
        });
    } catch (e) {
        console.error("Error al graficar reservas:", e);
    }
}