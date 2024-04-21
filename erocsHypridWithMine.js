function ch(y) {
  // Initialize prime table with pre-computed initial primes
  const primes = [2, 3, 5, 7];
  let counter = 0; // Initialize counter
  const isPrime = new Array(y + 1).fill(true); // Array to track primality

  // Sieve of Eratosthenes up to the square root of y
  for (let p = 2; p * p <= y; p++) {
    counter++; // Increment counter for each iteration of the outer loop
    if (isPrime[p]) {
      for (let i = p * p; i <= y; i += p) {
        counter++; // Increment counter for each iteration of the inner loop
        isPrime[i] = false; // Mark multiples of p as non-prime
      }
    }
  }
  // Apply additional primality testing for numbers beyond the square root of y
  for (let x = 11; x <= y; x++) {
    if (isPrime[x]) {
      // Use your primality testing method for further verification
      if (isPrimeNumber(x, primes)) {
        primes.push(x); // If prime, add to the list of primes
      }
      counter++; // Increment counter for each iteration of the verification step
    }
  }

  return { primes, counter }; // Return the list of primes and the total step count
}

// Function to test primality using additional method
function isPrimeNumber(x, primes) {
  const sqrtX = Math.floor(Math.sqrt(x));
  for (const prime of primes) {
    if (prime > sqrtX) {
      break;
    }
    if (x % prime === 0) {
      return false;
    }
  }
  return true;
}
