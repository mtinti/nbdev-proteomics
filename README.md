nbdev-proteomics
================

<!-- WARNING: THIS FILE WAS AUTOGENERATED! DO NOT EDIT! -->

A collection of utilities to process proteomics data

## Install

``` sh
pip install nbdev_proteomics
```

## How to use

Let’s start by uploading a dataset from a DIA-NN analysis

``` python
normalize_dataframe
```

    <function nbdev_proteomics.dim_red.normalize_dataframe(in_df)>

``` python
plot_mds_columns
```

    <function nbdev_proteomics.dim_red.plot_mds_columns(in_df, colors, color_to_label)>

``` python
impute_proteomics_data
```

    <function nbdev_proteomics.impute_missing.impute_proteomics_data(df, conditions)>

``` python
DatasetAnalysis()
```

    <nbdev_proteomics.core.DatasetAnalysis>

``` python
# Initialize the class with the Spectronaut output file
# and a table to rename the columns
#processor = SpectronautProcessor(
#    "../toy_datasets/spectronaut_output.tsv",
#    "../toy_datasets/spectronaut_column_mapping.tsv")

# Process the file and get the filtered protein quantification DataFrame
#filtered_quantification = processor.process()
#filtered_quantification.head()
```
