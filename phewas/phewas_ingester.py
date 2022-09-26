import tarfile

from os.path import exists

from phewas.phewas_association_pack import PhewasProgramArgs, PhewasAssociationPack
from runassociationtesting.ingest_data import *


class PhewasIngestData(IngestData):

    def __init__(self, parsed_options: PhewasProgramArgs):
        super().__init__(parsed_options)

        # Put additional options/covariate processing required by this specific package here
        is_snp_tar, is_gene_tar, tarball_prefixes = self._ingest_tarballs(parsed_options.association_tarballs)

        self._ingest_genetic_data(parsed_options.sparse_grm,
                                  parsed_options.sparse_grm_sample)

        # Put additional covariate processing specific to this module here
        self.set_association_pack(PhewasAssociationPack(self.get_association_pack(),
                                                        is_snp_tar, is_gene_tar, tarball_prefixes,
                                                        parsed_options.gene_ids))

    # Need to grab the tarball file for associations...
    # This was generated by the applet mrcepid-collapsevariants
    # Ingest the list file into this AWS instance
    @staticmethod
    def _ingest_tarballs(association_tarballs: dxpy.DXFile) -> Tuple[bool, bool, List[str]]:

        is_snp_tar = False
        is_gene_tar = False
        tarball_prefixes = []
        if '.tar.gz' in association_tarballs.describe()['name']:
            # likely to be a single tarball, download, check, and extract:
            tarball_name = association_tarballs.describe()['name']
            dxpy.download_dxfile(association_tarballs, tarball_name)
            if tarfile.is_tarfile(tarball_name):
                tarball_prefix = tarball_name.replace(".tar.gz", "")
                tarball_prefixes.append(tarball_prefix)
                tar = tarfile.open(tarball_name, "r:gz")
                tar.extractall()
                if exists(tarball_prefix + ".SNP.BOLT.bgen"):
                    is_snp_tar = True
                elif exists(tarball_prefix + ".GENE.BOLT.bgen"):
                    is_gene_tar = True
            else:
                raise dxpy.AppError(f'Provided association tarball ({association_tarballs.describe()["id"]}) '
                                    f'is not a tar.gz file')
        else:
            # Likely to be a list of tarballs, download and extract...
            dxpy.download_dxfile(association_tarballs, "tarball_list.txt")
            with open("tarball_list.txt", "r") as tarball_reader:
                for association_tarball in tarball_reader:
                    association_tarball = association_tarball.rstrip()
                    tarball = dxpy.DXFile(association_tarball)
                    tarball_name = tarball.describe()['name']
                    dxpy.download_dxfile(tarball, tarball_name)

                    # Need to get the prefix on the tarball to access resources within:
                    # All files within SHOULD have the same prefix as this file
                    tarball_prefix = tarball_name.rstrip('.tar.gz')
                    tarball_prefixes.append(tarball_prefix)
                    tar = tarfile.open(tarball_name, "r:gz")
                    tar.extractall()
                    if exists(tarball_prefix + ".SNP.BOLT.bgen"):
                        raise dxpy.AppError(f'Cannot run masks from a SNP list ({association_tarballs.describe()["id"]}) '
                                            f'when running tarballs as batch...')
                    elif exists(tarball_prefix + ".GENE.BOLT.bgen"):
                        raise dxpy.AppError(f'Cannot run masks from a GENE list ({association_tarballs.describe()["id"]}) '
                                            f'when running tarballs as batch...')

        return is_snp_tar, is_gene_tar, tarball_prefixes

    @staticmethod
    def _ingest_genetic_data(sparse_grm: dxpy.DXFile, sparse_grm_sample: dxpy.DXFile) -> None:
        # Now grab all genetic data that I have in the folder /project_resources/genetics/
        os.mkdir("genetics/")  # This is for legacy reasons to make sure all tests work...
        # This is the sparse matrix
        dxpy.download_dxfile(sparse_grm.get_id(),
                             'genetics/sparseGRM_470K_Autosomes_QCd.sparseGRM.mtx')
        dxpy.download_dxfile(sparse_grm_sample.get_id(),
                             'genetics/sparseGRM_470K_Autosomes_QCd.sparseGRM.mtx.sampleIDs.txt')
