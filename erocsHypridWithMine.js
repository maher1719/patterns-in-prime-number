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
function calculateChTimeComplexity(y) {
    return y * Math.sqrt(y / Math.log(y));
  }
  
  function calculateSTimeComplexity(y) {
    return y * Math.log(Math.log(Math.sqrt(y)));
  }
  function calculateSTimeComplexity2(y) {
    return 2*y+(y*Math.sqrt(y));
  }

  function chT(y) {
    return y * Math.sqrt(y / Math.log(y));
  }
  
  function sT(y) {
    return y * Math.log(Math.log(Math.sqrt(y)));
  }
  function sT2(y) {
    return 2*y+(y*Math.sqrt(y));
  }

  function diff(y){return [chT(y),sT(y),sT2(y)]}
  function isPrime(n) {
    if (n <= 1) return false;
    if (n <= 3) return true;
    if (n % 2 === 0 || n % 3 === 0) return false;

    let i = 5;
    while (i * i <= n) {
        if (n % i === 0 || n % (i + 2) === 0) return false;
        i += 6;
    }
    return true;
}

function countTwinPrimes(x, y) {
    let count = 0;
    let twins=[]
    for (let i = x; i <= y - 2; i++) {
        if (isPrime(i) && isPrime(i + 2)) {
            twins.push(i)
            twins.push(i+2)
            count++;
        }
    }
    return count;
}

const x = 10; // Starting number of the range
const y = 100; // Ending number of the range

const twinPrimeCount = countTwinPrimes(x, y);
console.log(`Number of twin prime numbers between ${x} and ${y}:`, twinPrimeCount);