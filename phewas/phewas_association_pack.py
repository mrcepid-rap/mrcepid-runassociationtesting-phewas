from dataclasses import dataclass
from typing import TypedDict, Dict, List

import dxpy

from runassociationtesting.association_pack import AssociationPack, ProgramArgs


@dataclass
class PhewasProgramArgs(ProgramArgs):
    association_tarballs: dxpy.DXFile
    bgen_index: dxpy.DXFile
    gene_ids: List[str]


# A TypedDict holding information about each chromosome's available genetic data
class BGENInformation(TypedDict):
    index: str
    sample: str
    bgen: str
    vep: str


class PhewasAssociationPack(AssociationPack):

    def __init__(self, association_pack: AssociationPack,
                 is_snp_tar: bool, is_gene_tar: bool, tarball_prefixes: List[str],
                 bgen_dict: Dict[str, BGENInformation], gene_ids: List[str]):

        super().__init__(association_pack.pheno_files, association_pack.inclusion_found,
                         association_pack.exclusion_found, association_pack.additional_covariates_found,
                         association_pack.is_binary, association_pack.sex, association_pack.threads,
                         association_pack.pheno_names,
                         association_pack.found_quantitative_covariates, association_pack.found_categorical_covariates)

        self.is_snp_tar = is_snp_tar
        self.is_gene_tar = is_gene_tar
        self.is_non_standard_tar = is_snp_tar or is_gene_tar
        self.tarball_prefixes = tarball_prefixes
        self.bgen_dict = bgen_dict
        self.gene_ids = gene_ids
