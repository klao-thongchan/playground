import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl

def analyze_excel_data(file_path, sheet_name='clean'):
    # Set font family that supports Unicode characters
    plt.rcParams['font.family'] = 'Arial Unicode MS'  # or try 'Microsoft YaHei' for Chinese
    
    # Read the Excel file
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    
    # Remove any non-numeric columns for correlation and clustering
    numeric_df = df.select_dtypes(include=[np.number])
    
    # Print information about numeric columns
    print("\nNumeric columns being analyzed:")
    print(numeric_df.columns.tolist())
    
    # Correlation Analysis
    correlation_matrix = numeric_df.corr()
    
    # Create correlation heatmap with smaller font size and figure size adjustment
    plt.figure(figsize=(12, 10))
    sns.heatmap(correlation_matrix, 
                annot=True, 
                cmap='coolwarm', 
                center=0,
                fmt='.2f',  # Round to 2 decimal places
                annot_kws={'size': 8})  # Smaller font size for annotations
    plt.title('Correlation Heatmap')
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    plt.savefig('correlation_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # K-means Clustering
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(numeric_df)
    
    # Determine optimal number of clusters using elbow method
    inertias = []
    K = range(1, 10)
    for k in K:
        kmeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(scaled_data)
        inertias.append(kmeans.inertia_)
    
    # Plot elbow curve
    plt.figure(figsize=(8, 6))
    plt.plot(K, inertias, 'bx-')
    plt.xlabel('k')
    plt.ylabel('Inertia')
    plt.title('Elbow Method For Optimal k')
    plt.savefig('elbow_curve.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Perform k-means with optimal k (let's use k=3 as an example)
    optimal_k = 3  # You can modify this based on elbow curve
    kmeans = KMeans(n_clusters=optimal_k, random_state=42)
    cluster_labels = kmeans.fit_predict(scaled_data)
    
    # Add cluster labels to original dataframe
    df['Cluster'] = cluster_labels
    
    # Save results - removed encoding parameter
    df.to_excel('clustered_data.xlsx', index=False)
    
    # Print column names for debugging
    print("\nAll columns in the dataset:")
    for col in df.columns:
        print(f"Column: {col}, Type: {type(col)}")
    
    return {
        'correlation_matrix': correlation_matrix,
        'cluster_labels': cluster_labels,
        'cluster_centers': kmeans.cluster_centers_,
        'original_data_with_clusters': df
    }

# Usage example
if __name__ == "__main__":
    # Replace with your file path
    file_path = "idol.xlsx"
    
    try:
        results = analyze_excel_data(file_path)
        
        # Print summary statistics for each cluster
        df_with_clusters = results['original_data_with_clusters']
        print("\nCluster Statistics:")
        for cluster in range(len(results['cluster_centers'])):
            print(f"\nCluster {cluster} Summary:")
            cluster_data = df_with_clusters[df_with_clusters['Cluster'] == cluster]
            print(f"Number of samples in cluster: {len(cluster_data)}")
            print(cluster_data.describe())
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        print("\nFull error traceback:")
        print(traceback.format_exc())