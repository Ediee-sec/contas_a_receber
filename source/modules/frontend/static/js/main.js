function updateFileName(input) {
    const fileName = document.getElementById('fileName');
    const fileError = document.getElementById('fileError');
    
    if (input.files.length > 0) {
        const file = input.files[0];
        if (file.name.endsWith('.xlsx')) {
            fileName.textContent = `📄 ${file.name}`;
            fileError.style.display = 'none';
        } else {
            fileName.textContent = '';
            fileError.textContent = '❌ Por favor, selecione apenas arquivos XLSX.';
            fileError.style.display = 'block';
            input.value = '';
        }
    } else {
        fileName.textContent = '';
    }
}

function formatTime(milliseconds) {
    const totalSeconds = Math.floor(milliseconds / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

async function handleSubmit(event) {
    event.preventDefault();
    
    const file = document.getElementById('file');
    const email = document.getElementById('email');
    const message = document.getElementById('message');
    const timer = document.getElementById('timer');
    const response = document.getElementById('response');
    
    document.querySelectorAll('.error').forEach(el => el.style.display = 'none');
    response.style.display = 'none';
    response.className = 'response';
    
    let isValid = true;

    // Validação do arquivo
    if (!file.files.length || !file.files[0].name.endsWith('.xlsx')) {
        document.getElementById('fileError').textContent = '❌ Por favor, selecione um arquivo XLSX.';
        document.getElementById('fileError').style.display = 'block';
        isValid = false;
    }

    // Validação do email
    if (!email.value || !email.value.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
        document.getElementById('emailError').textContent = '❌ Por favor, insira um e-mail válido.';
        document.getElementById('emailError').style.display = 'block';
        isValid = false;
    }

    // Validação da mensagem
    if (!message.value.trim()) {
        document.getElementById('messageError').textContent = '❌ Por favor, digite uma mensagem.';
        document.getElementById('messageError').style.display = 'block';
        isValid = false;
    }
    
    if (isValid) {
        // Iniciar o cronômetro
        const startTime = Date.now();
        timer.style.display = 'block';
        
        // Função para atualizar o cronômetro
        const timerInterval = setInterval(() => {
            const elapsedTime = Date.now() - startTime;
            timer.textContent = `Tempo de processamento: ${formatTime(elapsedTime)}`;
        }, 1000);

        const formData = new FormData();
        formData.append('file', file.files[0]);
        formData.append('email', email.value);
        formData.append('message', message.value);

        try {
            // Initial upload request
            const res = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            if (!res.ok) {
                throw new Error('Erro ao iniciar processamento');
            }

            const data = await res.json();
            const taskId = data.task_id;

            // Start polling for status
            while (true) {
                const statusRes = await fetch(`/status/${taskId}`);
                const statusData = await statusRes.json();

                if (statusData.status === 'completed') {
                    // Parar o cronômetro
                    clearInterval(timerInterval);
                    const totalTime = formatTime(Date.now() - startTime);
                    
                    response.innerHTML = `
                        <i class="fas fa-check-circle"></i> Arquivo processado com sucesso!<br>
                        Tempo total de processamento: ${totalTime}
                    `;
                    response.classList.add('success');
                    event.target.reset();
                    fileName.textContent = '';
                    break;
                } else if (statusData.status === 'error') {
                    throw new Error(statusData.message || 'Erro ao processar arquivo');
                } else if (statusData.status === 'not_found') {
                    throw new Error('Tarefa não encontrada');
                }

                // Wait before next poll
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
        } catch (error) {
            // Parar o cronômetro em caso de erro
            clearInterval(timerInterval);
            response.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${error.message}`;
            response.classList.add('error');
        } finally {
            timer.style.display = 'none';
            response.style.display = 'block';
        }
    }

    return false;
}