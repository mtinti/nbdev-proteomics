# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_impute_missing.ipynb.

# %% auto 0
__all__ = ['impute_proteomics_data']

# %% ../nbs/02_impute_missing.ipynb 3
from nbdev.showdoc import *
import numpy as np
import pandas as pd
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from scipy.stats import truncnorm

# %% ../nbs/02_impute_missing.ipynb 4
def impute_proteomics_data(df, conditions):
    
    def impute_detection_limit(condition_df, detection_limit):
        std_dev = detection_limit * 0.2

        def generate_positive_random_value(mean, std_dev):
            a, b = 0, np.inf
            return truncnorm.rvs(a=(a - mean) / std_dev, b=(b - mean) / std_dev, loc=mean, scale=std_dev)

        imputed_df = condition_df.applymap(lambda x: generate_positive_random_value(detection_limit, std_dev) if pd.isnull(x) else x)
        return imputed_df

    def compute_detection_limit(condition_df):
        smallest_values = []
        for column in condition_df.columns:
            column_data = condition_df[column]
            column_non_zero = column_data[column_data > 0]
            smallest_values.extend(column_non_zero.nsmallest(10).tolist())

        detection_limit = np.median(smallest_values)
        print('fill na with detection_limit:', detection_limit, np.log10(detection_limit),condition_df.columns)
        return detection_limit

    unique_conditions = set(conditions)
    imputed_dfs = []

    for condition in unique_conditions:
        condition_indices = [i for i, c in enumerate(conditions) if c == condition]
        condition_df = df.iloc[:, condition_indices]

        all_values_missing = condition_df.isnull().all(axis=1)
        missing_rows = condition_df[all_values_missing]
        non_missing_rows = condition_df[~all_values_missing]

        detection_limit = compute_detection_limit(condition_df)

        if not missing_rows.empty:
            imputed_missing_rows = impute_detection_limit(missing_rows, detection_limit)
        else:
            imputed_missing_rows = missing_rows
        
        #print(non_missing_rows)
        imp_mean = IterativeImputer(random_state=0, imputation_order='roman')
        
        imputed_data = imp_mean.fit_transform(non_missing_rows)
        imputed_data = np.maximum(imputed_data, detection_limit)
        #imputed_data = np.maximum(imputed_data, detection_limit * 0.1)
        
        imputed_non_missing_rows = pd.DataFrame(imputed_data,
                                                index=non_missing_rows.index,
                                                columns=non_missing_rows.columns)

        combined_df = pd.concat([imputed_missing_rows, imputed_non_missing_rows]).sort_index()
        imputed_dfs.append(combined_df)

    imputed_df = pd.concat(imputed_dfs, axis=1).reindex(columns=df.columns)
    return imputed_df
