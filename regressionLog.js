function getLogRegression(data, stepSize, steepness, rise) {
    const n = data.length;
    let sumX = 0,
      sumY = 0,
      sumXY = 0,
      sumXX = 0;
  
    for (let i = 0; i < n; i += stepSize) {
      const x = i + 1;
      const y = data[i]; // Assuming data is already in log form
      sumX += x;
      sumY += y;
      sumXY += x * y;
      sumXX += x * x;
    }
  
    const b = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
    const a = (sumY - b * sumX) / n;
  
    return (x) => a + b * x * steepness + rise;
  }
  
  