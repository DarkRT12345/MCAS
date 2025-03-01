import matplotlib.pyplot as plt

# Data for Precision and F1-Score
precision = [0.8678, 0.858, 0.8675, 0.8052, 0.8217]
f1_score = [0.8708, 0.8601, 0.8508, 0.8686, 0.8967]

# Labels for the x-axis (e.g., set numbers or indices)
x_labels = ['Set 1', 'Set 2', 'Set 3', 'Set 4', 'Set 5']

# Create the plot
plt.figure(figsize=(8, 6))
plt.plot(x_labels, precision, label='Precision', marker='o', linestyle='-', color='b')
plt.plot(x_labels, f1_score, label='F1-Score', marker='o', linestyle='-', color='g')

# Adding title and labels
plt.title('Precision and F1-Score for BERT')
plt.xlabel('Data Sets')
plt.ylabel('Score')
plt.legend()

# Display the plot
plt.grid(True)
plt.show()
