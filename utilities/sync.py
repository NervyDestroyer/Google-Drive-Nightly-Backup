import os
import glob
import shutil
import filecmp

# sync_folders
# Will sync two folders, copying files if not already modified (shutil.copy2 to preserve metadata)
# RECOMMENDED If shallow_comp=True, will just compare metadata (file type, size, and last modified)
def sync_folders(src, dst, shallow_comp=True):
    # Get every file in src dir
    files_needing_sync = get_files_needing_sync(src, dst, shallow_comp)

    # Go through each file and sync with the dst
    for (src_f, dst_f) in files_needing_sync:
        print("Syncing src=%s  dst=%s" % (src_f, dst_f))

        # Copy using shutil.copy2 to preserve metadata (so shallow comparison works correctly)
        (dst_head, dst_tail) = os.path.split(dst_f)
        if(not os.path.isdir(dst_head)):
            os.makedirs(dst_head)

        shutil.copy2(src_f, dst_f)

# get_files_needing_sync
# Gets the path for every file recursively in the given directory that requires a sync
# Returns the src file and the dst file. NOTE: dst file (and it's directories) may not exist
# Return format: [(src_f, dst_f), ...]
# RECOMMENDED If shallow_comp=True, will just compare metadata (file type, size, and last modified)
def get_files_needing_sync(src, dst, shallow_comp=True):
    files_to_sync = []

    src_files = [f for f in glob.glob("%s/**" % src, recursive=True) if os.path.isfile(f)]

    # Go through each file and determine if sync is needed
    for src_f in src_files:
        # Replace the src portion with the dst portion
        dst_f = src_f.replace(src, dst)

        # Determine if we need to do a copy (i.e. file not there, or not the same)
        need_sync = files_need_sync(src_f, dst_f, shallow_comp)

        if(need_sync):
            files_to_sync.append((src_f, dst_f))

    return files_to_sync


# files_need_sync
# Returns True if dst_f does not exist or is not the same as src_f, else returns False
# RECOMMENDED If shallow_comp=True, will just compare metadata (file type, size, and last modified)
def files_need_sync(src_f, dst_f, shallow_comp=True):
    if(os.path.isfile(dst_f)):
        return not filecmp.cmp(src_f, dst_f, shallow=True)
    else:
        return True
