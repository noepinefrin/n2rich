from typing import Dict
from scipy.stats import hypergeom, fisher_exact
from statsmodels.stats.multitest import multipletests

import json

class ConnectDB:

    """
    Connected DBS
    """

    __slots__ = ["selected_dbs"]

    def __init__(self, selected_dbs) -> None:
        self.selected_dbs = selected_dbs

    def _get_DBs_and_stats(self):
        dbs = {}
        dbs_stats = {}
        dbs_unique = {}
        try:
            db_path = f"./staticfiles/enrichment_db/enrichment_annotated/{self.selected_dbs}.json"
            db_stats_path = f"./staticfiles/enrichment_db/enrichment_db_stats/{self.selected_dbs}_db_stats.json"
            ## added
            db_unique_genes_path = f"./staticfiles/enrichment_db/enrichment_unique_gene_symbols/{self.selected_dbs}_db_unique.json"
        except:
            raise NameError('Database is not found.')
        dbs[self.selected_dbs] = self._open_db(path=db_path)
        dbs_stats[self.selected_dbs] = self._open_db(path=db_stats_path)

        ## added
        dbs_unique = self._open_db(path=db_unique_genes_path)

        return dbs, dbs_stats, dbs_unique  ## added

    def _open_db(self, path):
        with open(path, "r") as f:
            db = json.load(f)
        return db


class Enrichment:
    def __init__(
        self, g: list, dbs: Dict[str, dict], dbs_stats: dict, dbs_unique: dict
    ) -> None:
        self.g = set(g)
        self.dbs = dbs
        self.dbs_stats = dbs_stats
        self.dbs_unique = dbs_unique
        # self.selected_dbs = selected_dbs
        self.fishers_pvals = {}

    def response(self) -> dict:

        response = []

        for db_name, db_content in self.dbs.items():

            PT = self.dbs_stats[db_name]["PT"]

            PH = self._count_PH(g=self.g, dbs_unique=self.dbs_unique)

            if PH < 1:
                return "NO RESULT"

            for term, genes in db_content.items():

                if self._any_LH(genes=genes, g=self.g):

                    LT = self.dbs_stats[db_name]["LT"][term]

                    LH, LH_intersected = self._count_LH(genes=genes, g=self.g)

                    hypergeometric_pval = self._calc_hypergeometric_sf(LH, PT, LT, PH)

                    odds_ratio, fisher_exact_pval = self._calc_fishers_exact_test(
                        term, LH, PT, LT, PH
                    )

                    fold_enrichment = self._fold_enrichment(LH, PT, LT, PH)

                    response.extend(
                        [
                            [
                                term,
                                LH_intersected,
                                hypergeometric_pval,
                                odds_ratio,
                                fisher_exact_pval,
                                fold_enrichment,
                            ]
                        ]
                    )


            if not self.fishers_pvals.values():

                return "No Enrichment result."

            listed_fisherpval_values = list(self.fishers_pvals.values())

            _, adj_pvalues_bh, _, _ = multipletests(
                listed_fisherpval_values, alpha=0.05, method="fdr_bh"
            )

            for term, index in zip(
                self.fishers_pvals.keys(), range(len(listed_fisherpval_values))
            ):

                adj_pval_benjamini = "{:0.2E}".format(adj_pvalues_bh[index])

                response[index].extend([adj_pval_benjamini])

            self.fishers_pvals = {}
            listed_fisherpval_values = []

        return response

    def _count_PH(self, g: set, dbs_unique: dict) -> int:

        gene_coverage = list(dbs_unique.values())[0]

        PH = len(g.intersection(gene_coverage))
        return PH

    def _count_LH(self, genes, g: set) -> tuple:

        LH_intersected = list(set(genes).intersection(g))

        LH = len(LH_intersected)

        return (LH, LH_intersected)

    def _any_LH(self, genes, g: set) -> bool:
        return len(set(genes).intersection(g)) != 0

    def _calc_hypergeometric_sf(self, x, N, G, n) -> float:

        return "{:0.2E}".format(hypergeom.sf(x - 1, N, G, n))

    def _calc_fishers_exact_test(self, term, x, N, G, n) -> tuple:

        ct = [[0, 0],[0, 0]]

        ct[0][0] = x
        ct[0][1] = n - x
        ct[1][0] = G - x
        ct[1][1] = N - G - (n - x)

        odds_ratio, fishers_exact_pval = fisher_exact(ct, alternative="greater")

        self.fishers_pvals[term] = fishers_exact_pval

        return ("{:0.2f}".format(odds_ratio), "{:0.2E}".format(fishers_exact_pval))

    def _fold_enrichment(self, x, N, G, n) -> float:
        return "{:0.2f}".format((x / n) / (G / N))
