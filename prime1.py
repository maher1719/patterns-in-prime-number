import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
import scipy.stats as stats
from decimal import Decimal, getcontext

def prime_counting_function(x):
    """Function to count the number of primes less than or equal to x."""
    if x < 2:
        return 0
    sieve = np.ones(int(x) + 1, dtype=bool)
    sieve[0:2] = False
    for i in range(2, int(np.sqrt(x)) + 1):
        if sieve[i]:
            sieve[i*i:int(x)+1:i] = False
    return np.sum(sieve)

# Lire le fichier CSV
df = pd.read_csv('prime_data2.csv')
getcontext().prec = 50
print(f"Nombre total de lignes dans le fichier : {len(df)}")
df = df[(df['Number'] > 10) & (df['Number'] < 100)]
#df = df[(df['Number'] % 6 == 0) & (df['Number']<20000) ]
# Calculer pi(x) pour chaque valeur de x
# 
#df['pi_x'] = df['Number'].apply(prime_counting_function)*(math.pi/2)
number = df['Number']

# Calculate 'pi_x' based on the condition
df['pi_x'] = np.where(
    number < 10**3,
    df['Number'].apply(prime_counting_function)-(np.log(number)-np.log(np.log(number))),
    df['Number'].apply(prime_counting_function) - (np.e * np.log(number))#10^3
)

#df['pi_x'] = df['Number'].apply(lambda x: 1.675 * x / math.log(x))


# Créer le graphique
plt.figure(figsize=(12, 8))
plt.plot(df['Number'], df['pi_x'], label='pi(x)', color='red')
plt.plot(df['Number'], df['Primes +1'], label='Primes +1', color='blue', alpha=0.5)
plt.plot(df['Number'], df['Primes -1'], label='Primes -1', color='green', alpha=0.5)

plt.xlabel('x')
plt.ylabel('Valeur')
plt.title('Comparaison de pi(x) avec Primes +1 et Primes -1')
plt.legend()
plt.grid(True)

# Échelle logarithmique pour mieux voir les détails
plt.xscale('log')
plt.yscale('log')


plt.savefig('prime_pi_comparison.png')
plt.show()

# Calculer les ratios
df['ratio_plus_1'] = df['Primes +1'] / df['pi_x']
df['ratio_minus_1'] = df['Primes -1'] / df['pi_x']

# Afficher les statistiques des ratios
print("Statistiques pour le ratio (Primes +1) / pi(x):")
print(df['ratio_plus_1'].describe())
print("\nStatistiques pour le ratio (Primes -1) / pi(x):")
print(df['ratio_minus_1'].describe())

# Vérifier la convergence
last_1000_plus = df['ratio_plus_1'].tail(1000).mean()
last_1000_minus = df['ratio_minus_1'].tail(1000).mean()

print(f"\nMoyenne du ratio pour les 1000 dernières valeurs (Primes +1): {last_1000_plus:.20f}")
print(f"Moyenne du ratio pour les 1000 dernières valeurs (Primes -1): {last_1000_minus:.20f}")





from scipy.stats import ks_2samp

# Kolmogorov-Smirnov test for (Primes +1) vs pi(x)*(pi/2)
ks_stat_plus, ks_p_value_plus = ks_2samp(df['Primes +1'], df['pi_x'])
print(f"Kolmogorov-Smirnov test for (Primes +1) vs pi(x)*(pi/2):")
print(f"KS Statistic: {ks_stat_plus:.4f}, P-value: {ks_p_value_plus:.4f}")

# Kolmogorov-Smirnov test for (Primes -1) vs pi(x)*(pi/2)
ks_stat_minus, ks_p_value_minus = ks_2samp(df['Primes -1'], df['pi_x'])
print(f"\nKolmogorov-Smirnov test for (Primes -1) vs pi(x)*(pi/2):")
print(f"KS Statistic: {ks_stat_minus:.4f}, P-value: {ks_p_value_minus:.4f}")




from scipy.stats import anderson

# Anderson-Darling test for (Primes +1) / pi(x)*(pi/2)
anderson_stat_plus, critical_values_plus, significance_level_plus = anderson(df['ratio_plus_1'], dist='norm')
print(f"Anderson-Darling test for (Primes +1) / pi(x)*(pi/2):")
print(f"Anderson-Darling Statistic: {anderson_stat_plus:.4f}")
print(f"Critical Values: {critical_values_plus}")
print(f"Significance Levels: {significance_level_plus}")

# Anderson-Darling test for (Primes -1) / pi(x)*(pi/2)
anderson_stat_minus, critical_values_minus, significance_level_minus = anderson(df['ratio_minus_1'], dist='norm')
print(f"\nAnderson-Darling test for (Primes -1) / pi(x)*(pi/2):")
print(f"Anderson-Darling Statistic: {anderson_stat_minus:.4f}")
print(f"Critical Values: {critical_values_minus}")
print(f"Significance Levels: {significance_level_minus}")




from scipy.stats import levene

# Levene's test for (Primes +1) vs pi(x)*(pi/2)
levene_stat, levene_p_value = levene(df['Primes +1'], df['pi_x'])
print(f"Levene's test for variances:")
print(f"Levene Statistic: {levene_stat:.4f}, P-value: {levene_p_value:.4f}")


from scipy.stats import levene

# Levene's test for (Primes -1) vs pi(x)*(pi/2)
levene_stat, levene_p_value = levene(df['Primes -1'], df['pi_x'])
print(f"Levene's test for variances:")
print(f"Levene Statistic: {levene_stat:.4f}, P-value: {levene_p_value:.4f}")

