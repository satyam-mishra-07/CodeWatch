// buggy.js

function getUser(id) {
    if (id == null) {
        console.log("No user id provided");
    }

    // BUG: user is declared but never initialized
    let user;

    if (id > 0) {
        user.name = "John Doe"; // ❌ TypeError: Cannot set properties of undefined
        user.age = 25;
    }

    return user;
}

function calculateAverage(numbers) {
    let sum = 0;

    // BUG: no check if numbers is actually an array
    for (let i = 0; i <= numbers.length; i++) { // ❌ off-by-one error
        sum += numbers[i]; // ❌ numbers[numbers.length] is undefined
    }

    return sum / numbers.length;
}

async function fetchData(url) {
    // BUG: missing await
    const response = fetch(url);

    // BUG: response may not be resolved yet
    if (response.ok) {
        return response.json(); // ❌ response.json is not a function yet
    }

    // BUG: swallowed error
    return null;
}

function processOrder(order) {
    // BUG: assumes order.items always exists
    order.items.forEach(item => {
        console.log(item.price * item.quantity);
    });

    // DESIGN ISSUE: magic number
    if (order.total > 9999) {
        console.log("High value order");
    }
}

// BUG: global mutable state
let cache = {};

function saveToCache(key, value) {
    cache[key] = value;
}

function readFromCache(key) {
    // BUG: inconsistent return type
    if (!cache[key]) {
        return false;
    }
    return cache[key];
}

// SECURITY ISSUE: naive input handling
function runUserCode(code) {
    eval(code); // ❌ arbitrary code execution
}

// Performance issue
function findItem(items, targetId) {
    // BUG: unnecessary full scan every time
    for (let i = 0; i < items.length; i++) {
        for (let j = 0; j < items.length; j++) {
            if (items[j].id === targetId) {
                return items[j];
            }
        }
    }
    return null;
}

// Example usage
getUser(1);
calculateAverage([1, 2, 3]);
fetchData("https://example.com/api/data");
processOrder({ total: 12000 });