# House-Booking-Frontend
This is a project that is created by html,css and javascript for a house booking project especially for campus stydent who  usually find it hard to locate vaccant houses,especially when schools reopen 
<!-- ================= FRONTEND CODE ================= -->
<!-- register.html -->
<!-- Purpose: Allows student to register -->
<form id="registerForm">
  <input id="name" placeholder="Name" required />
  <input id="phone" placeholder="Phone" required />
  <input id="email" type="email" placeholder="Email" required />
  <input id="studentId" placeholder="Student ID" required />
  <input id="password" type="password" placeholder="Password" required />
  <button type="submit">Register</button>
</form>
<script>
document.getElementById('registerForm').addEventListener('submit', async function(e) {
  e.preventDefault();
  const formData = {
    name: document.getElementById('name').value,
    phone: document.getElementById('phone').value,
    email: document.getElementById('email').value,
    studentId: document.getElementById('studentId').value,
    password: document.getElementById('password').value
  };
  const res = await fetch('http://localhost:5000/api/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(formData)
  });
  const data = await res.json();
  alert(data.message);
});
</script>

<!-- login.html -->
<!-- Purpose: Allows student to log in -->
<form id="loginForm">
  <input id="email" type="email" placeholder="Email" required />
  <input id="password" type="password" placeholder="Password" required />
  <button type="submit">Login</button>
</form>
<script>
document.getElementById('loginForm').addEventListener('submit', async function(e) {
  e.preventDefault();
  const res = await fetch('http://localhost:5000/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: document.getElementById('email').value,
      password: document.getElementById('password').value
    })
  });
  const data = await res.json();
  if (data.token) {
    localStorage.setItem('token', data.token);
    window.location.href = 'dashboard.html';
  }
});
</script>

<!-- dashboard.html -->
<!-- Purpose: Show available house listings -->
<div id="housesList"></div>
<script>
const token = localStorage.getItem('token');
fetch('http://localhost:5000/api/houses', {
  headers: { 'Authorization': 'Bearer ' + token }
}).then(res => res.json()).then(houses => {
  houses.forEach(house => {
    const div = document.createElement('div');
    div.innerHTML = `
      <h3>${house.title}</h3>
      <p>${house.description}</p>
      <p>Price: ${house.price}</p>
      <p>Area: ${house.area}</p>
      <button onclick="bookHouse('${house._id}')">Book</button>
    `;
    document.getElementById('housesList').appendChild(div);
  });
});
</script>

<!-- booking.html -->
<!-- Purpose: Handle booking confirmation -->
<script>
function bookHouse(houseId) {
  const token = localStorage.getItem('token');
  const paymentConfirmation = prompt('Paste payment confirmation message (KES 100):');
  fetch('http://localhost:5000/api/bookings/book', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + token
    },
    body: JSON.stringify({ houseId, paymentConfirmation })
  })
  .then(res => res.json())
  .then(data => alert(data.message));
}
</script>

<!-- notifications.html -->
<!-- Purpose: Display vacancy notifications -->
<div id="notificationsList"></div>
<script>
fetch('http://localhost:5000/api/notifications/student', {
  headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }
})
.then(res => res.json())
.then(notes => {
  notes.forEach(note => {
    const div = document.createElement('div');
    div.innerHTML = `<strong>${note.area}</strong>: ${note.message}`;
    document.getElementById('notificationsList').appendChild(div);
  });
});
</script>

<!-- admin.html -->
<!-- Purpose: Admin can post house listings -->
<form id="houseForm">
  <input id="title" placeholder="Title" required />
  <input id="description" placeholder="Description" required />
  <input id="price" type="number" placeholder="Price" required />
  <input id="area" placeholder="Area" required />
  <input id="durationOptions" placeholder="Duration Options (e.g., One semester,Two semesters)" required />
  <button type="submit">Add House</button>
</form>
<script>
document.getElementById('houseForm').addEventListener('submit', async function(e) {
  e.preventDefault();
  const token = localStorage.getItem('token');
  const formData = {
    title: document.getElementById('title').value,
    description: document.getElementById('description').value,
    price: document.getElementById('price').value,
    area: document.getElementById('area').value,
    durationOptions: document.getElementById('durationOptions').value.split(',')
  };
  const res = await fetch('http://localhost:5000/api/admin/add-house', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + token
    },
    body: JSON.stringify(formData)
  });
  const data = await res.json();
  alert(data.message);
});
</script>

