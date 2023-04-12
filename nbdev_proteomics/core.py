# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_core.ipynb.

# %% auto 0
__all__ = ['DatasetViz', 'DatasetAnalysis', 'SpectronautProcessor', 'DIAnnProcessor']

# %% ../nbs/00_core.ipynb 4
class DatasetViz():
    """Class to visualize a data frame"""
    def __init__(self, df='', palette = False):
        self.df = df
        if not palette:
            self.palette = ['r']*df.shape[1]
        else:
            self.palette = palette
        
    def analyse_missing_values(self, figsize=(8, 4)):
        
        #visualization of missing data
        with plt.style.context('ggplot'):

            ax=msno.bar(self.df, figsize=figsize)
            # Set global font size to 8
            plt.rcParams['font.size'] = 8
            plt.rcParams['axes.titlesize'] = 8
            plt.rcParams['axes.labelsize'] = 8
            plt.rcParams['xtick.labelsize'] = 8
            plt.rcParams['ytick.labelsize'] = 8
            plt.rcParams['legend.fontsize'] = 8
            plt.rcParams['figure.titlesize'] = 8            
            
            plt.title('Missing Data Analysis', size=12)
            ax.set_ylabel('Fraction of data points',size=12)
            #plt.savefig(os.path.join(OUT_FOLDER,'1_missing_value_bar.png'))
            plt.tight_layout()
            plt.show()
            
            ax=msno.matrix(self.df, figsize=figsize)
            plt.tight_layout()
            plt.show()  
            
            
            ax=msno.dendrogram(self.df)
            plt.tight_layout()
            plt.show()
            
            
    def analyse_values_distribution(self,  figsize=(8, 4), do_log = True):
        fig,ax=plt.subplots(figsize=figsize)
        df = self.df
        
        if do_log:
            df = np.log10(df)
        
        df.plot(kind='kde', color=self.palette, alpha=0.5, ax=ax)   
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.title('Value Distribution')
        plt.xlabel('Intensity')
        plt.show()
        
        
        fig,ax=plt.subplots(figsize=figsize)
        sns.boxplot(data = df, showfliers=False, palette=self.palette,ax=ax)
        plt.title('Value Distribution')
        plt.xlabel('Sample')
        plt.ylabel('Intensity')
        plt.xticks(rotation=45,ha='right')
        plt.show()
        
        

# %% ../nbs/00_core.ipynb 6
class DatasetAnalysis():
    """Class to store common functions
    for the analysis of proteomics data"""
    
    #this function create from a table of:
    #old_column, condition, replica
    #a mepping dataframe. the condition and replica
    #are used to name the new column
    def parse_column_mapping(self, mapping_file):
        # Read the mapping file into a DataFrame
        if mapping_file.endswith('.csv'):
            mapping_df = pd.read_csv(mapping_file)
        else:    
            mapping_df = pd.read_csv(mapping_file, sep='\t')
        #print(mapping_df)
        # Assert that the DataFrame has at least 3 columns
        assert mapping_df.shape[1] >= 3

        # Replace '.IsSingleHit' with '.Quantity' in the 'col_name' column
        mapping_df['col_name'] = mapping_df['col_name'].str.replace('.IsSingleHit', '.Quantity')

        # Create a new column 'new_col' with the format 'condition.replica'
        mapping_df['new_col'] = mapping_df['condition'] + '.' + mapping_df['replica'].astype(str)

        # Create a dictionary mapping the original column names to the new column names
        mapping_dict = dict(zip(mapping_df['col_name'], mapping_df['new_col']))

        return mapping_dict 

    def replace_zeros(self, df):
        df = df.replace('0',0)
        df = df.replace(0,np.nan)
        return df              

# %% ../nbs/00_core.ipynb 7
class SpectronautProcessor(DatasetAnalysis):
    """Class to make a Spectronaut output
    ready for quntification"""
    def __init__(self, file_name='', column_mapping=''):
        self.filename = file_name
        self.column_mapping = self.parse_column_mapping(column_mapping)
        
    #prepare the dataset for analysis    
    def filter_protein_quantification(self, df):
        quant_cols = [n for n in df.columns if 'PG.Quantity' in n]

        # Create a mask DataFrame based on IsSingleHit columns
        mask = df[[n.replace('PG.Quantity', 'PG.IsSingleHit') for n in quant_cols]]
        mask.columns = quant_cols

        # Replace strings with their corresponding boolean values
        replacements = {'Filtered': True, 'False': False, 
                        'True': True, 'FALSE': False, 'TRUE': True}
        mask = mask.replace(replacements)

        # Get the data DataFrame with only the quantification columns
        selection = df[quant_cols]

        # Apply the mask to the data DataFrame
        filtered_selection = selection.mask(mask)
        filtered_selection = self.replace_zeros(filtered_selection)

        return filtered_selection
    

    #this function apply the logic of getting the dataframe
    #for quantification analysis
    def process(self):
        df = pd.read_csv(self.filename, sep="\t")
        filtered_quantification = self.filter_protein_quantification(df)
        filtered_quantification = filtered_quantification.rename(self.column_mapping,axis=1)
        return filtered_quantification


# %% ../nbs/00_core.ipynb 10
class DIAnnProcessor(DatasetAnalysis):
    """Class to make a DIA-NN output
    ready for quntification"""
    def __init__(self, file_name='', peptides_count='', column_mapping=''):
        self.filename = file_name
        self.column_mapping = self.parse_column_mapping(column_mapping)
        self.peptides_count = peptides_count
        
    def filter_protein_quantification(self, df):
        #we use only the protein identified at least with 2
        #peptides
        df_peptide = pd.read_csv(self.peptides_count, sep='\t')
        #name from the R script used to create the peptide count file
        df_peptide.set_index('Var1',inplace=True)
        good_quant = df_peptide[df_peptide['Freq']>=2]
        filtered_selection=df.loc[good_quant.index.values]
        filtered_selection = self.replace_zeros(filtered_selection)
        return filtered_selection

    def fix_col_names(self, df):
        '''
        DIA-NN processes raw files in random order. The column names
        contains the full path to the analysed file. this function clean
        the column names and order the columns based on the order in
        the column_mapping dictionary
        '''
        #grab the last part shuld be protein name
        cols = [n.split('\\')[-1] for n in df.columns]
        #remove .dia, if raw files has been
        #transformed to .dia
        cols = [n.replace('.dia','') for n in cols]
        df.columns = cols
        return df
    
    #this function apply the logic of getting the dataframe
    #ready for quantification analysis
    def process(self):
        df = pd.read_csv(self.filename, sep="\t")
        filtered_quantification = self.filter_protein_quantification(df)
        filtered_quantification = self.fix_col_names(filtered_quantification)
        filtered_quantification = filtered_quantification.rename(self.column_mapping,axis=1)
        filtered_quantification = filtered_quantification[self.column_mapping.values()]
        return filtered_quantification

