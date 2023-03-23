# To process the G-NAF data
# November 2022

import pandas as pd
from datetime import datetime
import numpy as np


folderPath = r"/mnt/c/Users/Engineer/Desktop/Github Projects/dataCollection/australianAddress/G-NAF/G-NAF NOVEMBER 2022/Standard/"
stateList = ["ACT"] #, "NSW", "NT", "OT", "QLD", "SA", "TAS", "VIC", "WA"

index_state = 0

ADDRESS_DETAIL_psv_full = []

while index_state < len(stateList):

    state = stateList[index_state]

    ADDRESS_ALIAS_psv = pd.read_csv(folderPath + state + "_ADDRESS_ALIAS_psv.psv", delimiter="|", low_memory=False)
    ADDRESS_DEFAULT_GEOCODE_psv = pd.read_csv(folderPath + state + "_ADDRESS_DEFAULT_GEOCODE_psv.psv", delimiter="|", low_memory=False)
    ADDRESS_DETAIL_psv = pd.read_csv(folderPath + state + "_ADDRESS_DETAIL_psv.psv", delimiter="|", low_memory=False)
    ADDRESS_FEATURE_psv = pd.read_csv(folderPath + state + "_ADDRESS_FEATURE_psv.psv", delimiter="|", low_memory=False)
    ADDRESS_MESH_BLOCK_2016_psv = pd.read_csv(folderPath + state + "_ADDRESS_MESH_BLOCK_2016_psv.psv", delimiter="|", low_memory=False)
    ADDRESS_MESH_BLOCK_2021_psv = pd.read_csv(folderPath + state + "_ADDRESS_MESH_BLOCK_2021_psv.psv", delimiter="|", low_memory=False)
    ADDRESS_SITE_GEOCODE_psv = pd.read_csv(folderPath + state + "_ADDRESS_SITE_GEOCODE_psv.psv", delimiter="|", low_memory=False)
    ADDRESS_SITE_psv = pd.read_csv(folderPath + state + "_ADDRESS_SITE_psv.psv", delimiter="|", low_memory=False)
    LOCALITY_ALIAS_psv = pd.read_csv(folderPath + state + "_LOCALITY_ALIAS_psv.psv", delimiter="|", low_memory=False)
    LOCALITY_NEIGHBOUR_psv = pd.read_csv(folderPath + state + "_LOCALITY_NEIGHBOUR_psv.psv", delimiter="|", low_memory=False)
    LOCALITY_POINT_psv = pd.read_csv(folderPath + state + "_LOCALITY_POINT_psv.psv", delimiter="|", low_memory=False)
    LOCALITY_psv = pd.read_csv(folderPath + state + "_LOCALITY_psv.psv", delimiter="|", low_memory=False)
    MB_2016_psv = pd.read_csv(folderPath + state + "_MB_2016_psv.psv", delimiter="|", low_memory=False)
    MB_2021_psv = pd.read_csv(folderPath + state + "_MB_2021_psv.psv", delimiter="|", low_memory=False)
    PRIMARY_SECONDARY_psv = pd.read_csv(folderPath + state + "_PRIMARY_SECONDARY_psv.psv", delimiter="|", low_memory=False)
    STATE_psv = pd.read_csv(folderPath + state + "_STATE_psv.psv", delimiter="|", low_memory=False)
    STREET_LOCALITY_ALIAS_psv = pd.read_csv(folderPath + state + "_STREET_LOCALITY_ALIAS_psv.psv", delimiter="|", low_memory=False)
    STREET_LOCALITY_POINT_psv = pd.read_csv(folderPath + state + "_STREET_LOCALITY_POINT_psv.psv", delimiter="|", low_memory=False)
    STREET_LOCALITY_psv = pd.read_csv(folderPath + state + "_STREET_LOCALITY_psv.psv", delimiter="|", low_memory=False)

    ADDRESS_DETAIL_psv_full = pd.merge(ADDRESS_DETAIL_psv, ADDRESS_DEFAULT_GEOCODE_psv[["ADDRESS_DETAIL_PID", "LONGITUDE", "LATITUDE"]], \
                                       how="left", left_on="ADDRESS_DETAIL_PID", right_on="ADDRESS_DETAIL_PID")

    ADDRESS_DETAIL_psv_full = pd.merge(ADDRESS_DETAIL_psv_full, STREET_LOCALITY_psv[["STREET_LOCALITY_PID", "STREET_NAME", "STREET_TYPE_CODE"]], \
                                       how="left", left_on="STREET_LOCALITY_PID", right_on="STREET_LOCALITY_PID")

    ADDRESS_DETAIL_psv_full = pd.merge(ADDRESS_DETAIL_psv_full, LOCALITY_psv[["LOCALITY_PID", "LOCALITY_NAME"]], \
                                       how="left", left_on="LOCALITY_PID", right_on="LOCALITY_PID")

    ADDRESS_DETAIL_psv_full["State"] = state


    # if index_state == 0:
    #     ADDRESS_DETAIL_psv_full = ADDRESS_DETAIL_psv
    # else:
    #     ADDRESS_DETAIL_psv_full = pd.concat([ADDRESS_DETAIL_psv_full, ADDRESS_DETAIL_psv])
    
    index_state += 1

ADDRESS_DETAIL_psv_full["Full Address"] = np.where(ADDRESS_DETAIL_psv_full["LOT_NUMBER_PREFIX"].notna(), ADDRESS_DETAIL_psv_full["LOT_NUMBER_PREFIX"].astype(str) + " ", "") + \
                                          np.where(ADDRESS_DETAIL_psv_full["LOT_NUMBER"].notna(), ADDRESS_DETAIL_psv_full["LOT_NUMBER"].astype(str).str.split(".").str[0] + " ", "") + \
                                          np.where(ADDRESS_DETAIL_psv_full["LOT_NUMBER_SUFFIX"].notna(), ADDRESS_DETAIL_psv_full["LOT_NUMBER_SUFFIX"].astype(str) + " ", "") + \
                                          np.where(ADDRESS_DETAIL_psv_full["FLAT_TYPE_CODE"].notna(), ADDRESS_DETAIL_psv_full["FLAT_TYPE_CODE"] + " ", "") + \
                                          np.where(ADDRESS_DETAIL_psv_full["FLAT_NUMBER_PREFIX"].notna(), ADDRESS_DETAIL_psv_full["FLAT_NUMBER_PREFIX"].astype(str).str.split(".").str[0] + " ", "") + \
                                          np.where(ADDRESS_DETAIL_psv_full["FLAT_NUMBER"].notna(), ADDRESS_DETAIL_psv_full["FLAT_NUMBER"].astype(str).str.split(".").str[0] + " ", "") + \
                                          np.where(ADDRESS_DETAIL_psv_full["FLAT_NUMBER_SUFFIX"].notna(), ADDRESS_DETAIL_psv_full["FLAT_NUMBER_SUFFIX"].astype(str).str.split(".").str[0] + " ", "") + \
                                          np.where(ADDRESS_DETAIL_psv_full["LEVEL_TYPE_CODE"].notna(), ADDRESS_DETAIL_psv_full["LEVEL_TYPE_CODE"] + " ", "") + \
                                          np.where(ADDRESS_DETAIL_psv_full["LEVEL_NUMBER_PREFIX"].notna(), ADDRESS_DETAIL_psv_full["LEVEL_NUMBER_PREFIX"].astype(str) + " ", "") + \
                                          np.where(ADDRESS_DETAIL_psv_full["LEVEL_NUMBER"].notna(), ADDRESS_DETAIL_psv_full["LEVEL_NUMBER"].astype(str).str.split(".").str[0] + " ", "") + \
                                          np.where(ADDRESS_DETAIL_psv_full["LEVEL_NUMBER_SUFFIX"].notna(), ADDRESS_DETAIL_psv_full["LEVEL_NUMBER_SUFFIX"].astype(str) + " ", "") + \
                                          np.where(ADDRESS_DETAIL_psv_full["NUMBER_FIRST_PREFIX"].notna(), ADDRESS_DETAIL_psv_full["NUMBER_FIRST_PREFIX"].astype(str) + " ", "") + \
                                          np.where(ADDRESS_DETAIL_psv_full["NUMBER_FIRST"].notna(), ADDRESS_DETAIL_psv_full["NUMBER_FIRST"].astype(str).str.split(".").str[0] + " ", "") + \
                                          np.where(ADDRESS_DETAIL_psv_full["NUMBER_FIRST_SUFFIX"].notna(), ADDRESS_DETAIL_psv_full["NUMBER_FIRST_SUFFIX"].astype(str) + " ", "") + \
                                          np.where(ADDRESS_DETAIL_psv_full["NUMBER_LAST_PREFIX"].notna(), ADDRESS_DETAIL_psv_full["NUMBER_LAST_PREFIX"].astype(str) + " ", "") + \
                                          np.where(ADDRESS_DETAIL_psv_full["NUMBER_LAST"].notna(), "- " + ADDRESS_DETAIL_psv_full["NUMBER_LAST"].astype(str).str.split(".").str[0] + " ", "") + \
                                          np.where(ADDRESS_DETAIL_psv_full["NUMBER_LAST_SUFFIX"].notna(), ADDRESS_DETAIL_psv_full["NUMBER_LAST_SUFFIX"].astype(str) + " ", "") + \
                                          ADDRESS_DETAIL_psv_full["STREET_NAME"] + " " + \
                                          np.where(ADDRESS_DETAIL_psv_full["STREET_TYPE_CODE"].notna(), ADDRESS_DETAIL_psv_full["STREET_TYPE_CODE"] + " ", "") + \
                                          ADDRESS_DETAIL_psv_full["LOCALITY_NAME"] + " " + ADDRESS_DETAIL_psv_full["State"]


ADDRESS_DETAIL_psv_full.to_csv(r"/mnt/c/Users/Engineer/Desktop/Github Projects/dataCollection/australianAddress/temp_{}.csv".format(datetime.today().strftime('%Y-%m-%d')), index=False)