    document.getElementById('registerForm').addEventListener('submit', async function(e) {
      e.preventDefault();
      const formData = {
        name: name.value,
        phone: phone.value,
        email: email.value,
        studentId: studentId.value,
        password: password.value
      };
      const res = await fetch('http://localhost:5000/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      const data = await res.json();
      alert(data.message);
    });
