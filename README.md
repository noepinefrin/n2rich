# N2Rich: A Web-Based Gene-Enrichment and Functional Annotation Tool
N2Rich is a sophisticated web-based bioinformatics tool designed for gene-enrichment and functional annotation purposes. It has been meticulously implemented from scratch, following the detailed instructions provided by [DAVID](https://david.ncifcrf.gov/content.jsp?file=functional_annotation.html).

## Implementation Details
The tool's implementation involves several crucial steps. Firstly, it calculates the Population Total (PT) and List Total (LT) for every Database, where PT represents the number of unique genes existing per database, and LT represents the number of genes per term. These pre-calculated values are stored for efficient retrieval.

Subsequently, Population Hit (PH) and List Hit (LH) are calculated. PH represents the intersection of user-submitted genes and unique genes in the database, utilizing unique genes to account for commonality among terms. LH represents the intersection of user-submitted genes and the current term in the database. The exact code for this implementation can be found in enrichment/enrichment.py.

To illustrate with an example, the Fisher's Exact test is employed, requiring the creation of a 2x2 contingency table, as shown below:

2x2 Contingency Table
---------------------

| /  | User submitted genes | Genome | Total |
| ------------- | ------------- | ------------- |  ------------- |
| In Pathway  | LH  | PH - LH | PH |
| Not In Pathway | LT-LH  | PT - LT - PH + LH | PT - PH|
| Total | LT | PT - LT | PT |

Example:
-------
Assuming the user submitted 35 genes, the term in the database includes 63 genes, and the intersection of user-submitted genes and the term is 7, with 12,000 unique genes in the Pathway DB, and 19 genes intersected in the Pathway DB. The corresponding values for this example are 
```python
LT = 63 # List Total
LH = 7 # List Hit
PT = 12000 # Population Total
PH = 19 # Population Hit
```


In the table
---------------------

| / | User submitted genes | Genome | Total |
| ------------- | ------------- | ------------- |  ------------- |
| In Pathway  | 7  | 12 | 19 |
| Not In Pathway | 56  | 11925 | 11981 |
| Total | 63 | 11937 | 12000 |

Then, Fisher's Exact p-value = 3.74e-12. Since p-value < 0.05, this user's gene list is specifically associated (enriched) in the p53 signaling pathway by more than random chance.

In addition to the Fisher's Exact test, the tool provides Hypergeometric Survival Function, Benjamini/Hochberg (adjusted p-value), and Fold Enrichment score.

```python
from scipy.stats import hypergeom, fisher_exact
from statsmodels.stats.multitest import multipletests

hypergeometric_pval = self._calc_hypergeometric_sf(LH, PT, LT, PH)

odds_ratio, fisher_exact_pval = self._calc_fishers_exact_test(
                    term, LH, PT, LT, PH
                )

fold_enrichment = self._fold_enrichment(LH, PT, LT, PH)

_, adj_pvalues_bh, _, _ = multipletests(
            listed_fisherpval_values, alpha=0.05, method="fdr_bh"
                )
```

The Fold Enrichment score is defined as LH/PH divided by LT/PT. In simple terms, it provides the ratio of Hits to Totals, with a higher value indicating is mostly better.

```python
def _fold_enrichment(self, x, N, G, n) -> float:
        """
        Calculate fold enrichment score, get hits / total ratio.
        
        Parameters
        ----------
        x: List Hits (LH)
        n: Population Hits (PH)
        N: Population Total (PT)
        G: List Total (LT)

        Returns
        -------
        2 significant figured float. ex: 45.76
        """
        return "{:0.2f}".format((x / n) / (G / N))
```


Contact
-------
For any inquiries or questions regarding N2Rich or its functionalities, please feel free to contact me directly. I can be reached via email at berkayozcelik77@hotmail.com or through my LinkedIn profile at [LinkedIn](linkedin.com/in/berkay-ozcelik/).
