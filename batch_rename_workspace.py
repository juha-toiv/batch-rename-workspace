# Copyright (c) 2022 Juha
# Licensed under the terms of the MIT License

import arcpy
import time
import re


class BatchRenameWorkspaceException(Exception):
    error_msg = ""

    def __init__(self, error_msg, *args):
        super().__init__(args)
        self.error_msg = error_msg

    def __str__(self):
        return 'Exception: ' + self.error_msg


def count_true_values(l):
	return sum(bool(i) for i in l)


if __name__ == '__main__':
    ws = arcpy.GetParameterAsText(0)
    is_ds = arcpy.GetParameter(1)
    is_fc = arcpy.GetParameter(2)
    is_field_name = arcpy.GetParameter(3)
    is_field_alias = arcpy.GetParameter(4)
    repl_alias_underscore_with_space = arcpy.GetParameter(5)
    reg = arcpy.GetParameterAsText(6)
    is_lowercase = arcpy.GetParameter(7)
    is_uppercase = arcpy.GetParameter(8)
    is_title = arcpy.GetParameter(9)
    is_sentence = arcpy.GetParameter(10)
    repl = arcpy.GetParameterAsText(11)
    repl_with = arcpy.GetParameterAsText(12)
    remove_first_n = arcpy.GetParameter(13)
    remove_last_n = arcpy.GetParameter(14)
    add_prefix = arcpy.GetParameterAsText(15)
    add_suffix = arcpy.GetParameterAsText(16)

    if not is_field_alias and repl_alias_underscore_with_space:
        err_msg = "Error - field alias not selected"
        arcpy.AddError(err_msg)
        raise BatchRenameWorkspaceException(err_msg)

    if count_true_values([is_ds, is_fc, is_field_name, is_field_alias]) == 0:
        err_msg = "Error - no dataset type selected"
        arcpy.AddError(err_msg)
        raise BatchRenameWorkspaceException(err_msg)

    if count_true_values([is_lowercase, is_title, is_uppercase, is_sentence]) > 1:
        err_msg = "Error - select either lowercase, title case, uppercase or none"
        arcpy.AddError(err_msg)
        raise BatchRenameWorkspaceException(err_msg)

    if repl == "" and repl_with != "":
        err_msg = "Error - 'Replace' cannot be an empty string"
        arcpy.AddError(err_msg)
        raise BatchRenameWorkspaceException(err_msg)

    special_characters = " !@#$%^&*()-=+,./<>?[]{}\|`~"

    if (any((c in special_characters) for c in repl_with)) or (any((c in special_characters) for c in add_prefix)) or (any((c in special_characters) for c in add_suffix)):
        if is_fc or is_ds or is_field_name:
            err_msg = "Error - feature class or feature dataset or field names cannot contain any empty spaces or special characters except an underscore"
            arcpy.AddError(err_msg)
            raise BatchRenameWorkspaceException(err_msg)

    if add_prefix != "":
        if is_fc or is_ds or is_field_name:
            if add_prefix[0].isnumeric() or add_prefix[0] == "_":
                err_msg = "Error - first character cannot be a number or an underscore"
                arcpy.AddError(err_msg)
                raise BatchRenameWorkspaceException(err_msg)

    arcpy.env.workspace = ws

    datasets = arcpy.ListDatasets(feature_type='Feature')
    datasets = [''] + datasets if datasets is not None else []

    try:
        for ds in datasets:
            old_nm = ds
            tmp_nm = ds
            if is_ds and ds != "":
                if reg == "" or (reg != "" and re.search(r'{0}}'.format(reg), ds)):
                    if repl != "":
                        tmp_nm = tmp_nm.replace(repl, repl_with)
                    if is_uppercase:
                        tmp_nm = tmp_nm.upper()
                    if is_lowercase:
                        tmp_nm = tmp_nm.lower()
                    if is_title:
                        tmp_nm = tmp_nm.replace("_", " ").title().replace(" ", "_")
                    if is_sentence:
                        tmp_nm = tmp_nm.capitalize()
                    if remove_first_n != "":
                        tmp_nm = tmp_nm[int(remove_first_n):]
                    if remove_last_n != "":
                        tmp_nm = tmp_nm[:int(remove_last_n)]
                    if add_prefix != "":
                        tmp_nm = add_prefix + tmp_nm
                    if add_suffix != "":
                        tmp_nm = tmp_nm + add_suffix
                    tmp_nm = "tmp_" + tmp_nm.strip()
                    arcpy.Rename_management(old_nm, tmp_nm, "FeatureDataset")
                    arcpy.Rename_management(tmp_nm, tmp_nm[4:].strip(), "FeatureDataset")
            features = arcpy.ListFeatureClasses(feature_dataset=ds)
            for fc in features:
                if is_field_name or is_field_alias:
                    field_list = arcpy.ListFields(fc)
                    for f in field_list:
                        if f.editable and f.name not in ["OBJECTID", "FID", "Shape", "Shape_Length", "Shape_Area", "GLOBALID"]:
                            old_nm = f.name
                            tmp_nm = f.name
                            new_nm = f.name
                            old_alias = f.aliasName
                            tmp_alias = f.aliasName
                            new_alias = f.aliasName
                            if is_field_name:
                                if reg == "" or (reg != "" and re.search(r'{0}}'.format(reg), f.name)):
                                    if is_field_name:
                                        if repl != "":
                                            tmp_nm = tmp_nm.replace(repl, repl_with)
                                        if is_uppercase:
                                            tmp_nm = tmp_nm.upper()
                                        if is_lowercase:
                                            tmp_nm = tmp_nm.lower()
                                        if is_title:
                                            tmp_nm = tmp_nm.replace("_", " ").title().replace(" ", "_")
                                        if is_sentence:
                                            tmp_nm = tmp_nm.capitalize()
                                        if remove_first_n != "":
                                            tmp_nm = tmp_nm[int(remove_first_n):]
                                        if remove_last_n != "":
                                            tmp_nm = tmp_nm[:int(remove_last_n)]
                                        if add_prefix != "":
                                            tmp_nm = add_prefix + tmp_nm
                                        if add_suffix != "":
                                            tmp_nm = tmp_nm + add_suffix
                                        tmp_nm = "tmp_" + tmp_nm.strip()
                                        arcpy.AlterField_management(fc, old_nm, tmp_nm)
                                        new_nm = tmp_nm[4:].strip()
                                        time.sleep(1)
                                        if (is_field_alias):
                                            new_alias = new_nm
                                            if repl_alias_underscore_with_space:
                                                new_alias = new_alias.replace("_", " ").strip()
                                            arcpy.AlterField_management(fc, tmp_nm, new_nm, new_alias)
                                        else:
                                            arcpy.AlterField_management(fc, tmp_nm, new_nm)
                                if not is_field_name and is_field_alias:
                                    if repl != "":
                                        new_alias.replace(repl, repl_with)
                                    if is_uppercase:
                                        new_alias = new_alias.upper()
                                    if is_lowercase:
                                        new_alias = new_alias.lower()
                                    if is_title:
                                        new_alias = new_alias.replace("_", " ").title().replace(" ", "_")
                                    if is_sentence:
                                        new_alias = new_alias.capitalize()
                                    if remove_first_n != "":
                                        new_alias = new_alias[int(remove_first_n):]
                                    if remove_last_n != "":
                                        new_alias = new_alias[:int(remove_last_n)]
                                    if add_prefix != "":
                                        new_alias = add_prefix + new_alias
                                    if add_suffix != "":
                                        new_alias = new_alias + add_suffix
                                    if repl_alias_underscore_with_space:
                                        new_alias = new_alias.replace("_", " ").strip()
                                    arcpy.AlterField_management(fc, new_field_alias=new_alias)
            if is_fc:
                if reg == "" or (reg != "" and re.search(r'{0}}'.format(reg), fc)):
                    old_nm = fc
                    tmp_nm = fc
                    if repl != "":
                        tmp_nm = tmp_nm.replace(repl, repl_with)
                    if is_uppercase:
                        tmp_nm = tmp_nm.upper()
                    if is_lowercase:
                        tmp_nm = tmp_nm.lower()
                    if is_title:
                        tmp_nm = tmp_nm.replace("_", " ").title().replace(" ", "_")
                    if is_sentence:
                        tmp_nm = tmp_nm.capitalize()
                    if remove_first_n != "":
                        tmp_nm = tmp_nm[int(remove_first_n):]
                    if remove_last_n != "":
                        tmp_nm = tmp_nm[:int(remove_last_n)]
                    if add_prefix != "":
                        tmp_nm = add_prefix + tmp_nm
                    if add_suffix != "":
                        tmp_nm = tmp_nm + add_suffix
                    tmp_nm = "tmp_" + tmp_nm.strip()
                    try:
                        arcpy.Rename_management(old_nm, tmp_nm, "FeatureClass")
                        new_nm = tmp_nm[4:].strip()
                        arcpy.Rename_management(tmp_nm, new_nm, "FeatureClass")
                    except:
                        pass
    except Exception as e:
        arcpy.AddError(e)
        raise BatchRenameWorkspaceException(e)
