const API_BASE = "http://localhost:8000/api";
let pollInterval = null;

document.getElementById('scan-btn').addEventListener('click', async () => {
    const qrCode = document.getElementById('qr-input').value.trim();
    if (!qrCode) return;
    
    if (pollInterval) {
        clearInterval(pollInterval);
    }
    
    const resultCard = document.getElementById('result-card');
    const resultTitle = document.getElementById('result-title');
    const resultMessage = document.getElementById('result-message');
    const attendeeDetails = document.getElementById('attendee-details');
    
    resultCard.className = 'card';
    attendeeDetails.innerHTML = '';
    
    try {
        const response = await fetch(`${API_BASE}/checkin`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ qr_code: qrCode })
        });
        
        const data = await response.json();
        
        if (response.ok && data.status === "PENDING_PRINT") {
            resultCard.classList.add('pending');
            resultTitle.textContent = "Printing Badge...";
            resultMessage.textContent = "Your request has been queued. Please wait.";
            attendeeDetails.innerHTML = `
                <p><strong>Name:</strong> ${data.attendee.full_name}</p>
                <p><strong>Ticket:</strong> ${data.attendee.ticket_type}</p>
                <p><strong>Status:</strong> ${data.attendee.status}</p>
            `;
            
            pollInterval = setInterval(async () => {
                try {
                    const pollRes = await fetch(`${API_BASE}/attendee/${qrCode}`);
                    if (pollRes.ok) {
                        const pollData = await pollRes.json();
                        if (pollData.status === "CHECKED_IN") {
                            clearInterval(pollInterval);
                            resultCard.className = 'card success';
                            resultTitle.textContent = "Checked In / Badge Printed";
                            resultMessage.textContent = "Check-in finalized via printer webhook callback";
                            attendeeDetails.innerHTML = `
                                <p><strong>Name:</strong> ${pollData.full_name}</p>
                                <p><strong>Ticket:</strong> ${pollData.ticket_type}</p>
                                <p><strong>Status:</strong> ${pollData.status}</p>
                                <p><strong>Issued At:</strong> ${pollData.checked_in_at}</p>
                            `;
                            refreshDirectory();
                        }
                    }
                } catch (err) {
                    console.error("Polling error", err);
                }
            }, 400);
            
        } else if (!response.ok) {
            resultCard.classList.add('error');
            resultTitle.textContent = "Duplicate Scan / Access Denied";
            resultMessage.textContent = data.detail || "Error occurred";
        }
        
        refreshDirectory();
    } catch (error) {
        resultCard.classList.add('error');
        resultTitle.textContent = "System Error";
        resultMessage.textContent = error.message;
    }
});

async function refreshDirectory() {
    try {
        const response = await fetch(`${API_BASE}/attendees`);
        const attendees = await response.json();
        
        const tbody = document.querySelector('#directory-table tbody');
        tbody.innerHTML = '';
        
        attendees.forEach(att => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${att.id}</td>
                <td>${att.qr_code}</td>
                <td>${att.full_name}</td>
                <td>${att.ticket_type}</td>
                <td>${att.status}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error("Failed to refresh directory", error);
    }
}

refreshDirectory();
