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

    function bookHouse(houseId) {
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
