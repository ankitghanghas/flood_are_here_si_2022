import sys
import rasterio as rio

path = sys.argv[1]

with rio.open(path) as ds_in:
    in_tif = ds_in.read(1, masked=True)
    in_tif_profile = ds_in.profile

in_tif_profile["compress"] = "lzw"
w_msk = (~in_tif.mask * 255).astype("uint8")
# write raster with internal mask (no .msk sidecar)
with rio.Env(GDAL_TIFF_INTERNAL_MASK=True):
    with rio.open(f"{path[:-4]}_lzw.tif", "w", **in_tif_profile) as ds_out:
        ds_out.write(in_tif, 1)
        ds_out.write_mask(w_msk)
