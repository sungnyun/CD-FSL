import glob
import os
import re
from argparse import Namespace

import configs

DATASET_KEYS = {
    'miniImageNet': 'mini',
    'miniImageNet_test': 'mini_test',
    'tieredImageNet': 'tiered',
    'CropDisease': 'crop',
    'EuroSAT': 'euro',
    'ISIC': 'isic',
    'ChestX': 'chest',
}

BACKBONE_KEYS = {
    'resnet10': 'resnet10',
    'resnet18': 'resnet18',
}

MODEL_KEYS = {
    'base': 'base',
    'simclr': 'simclr',
    'simsiam': 'simsiam',
    'moco': 'moco',
    'swav': 'swav',
    'byol': 'byol',
}


def get_output_directory(params: Namespace, previous_step=False, makedirs=True):
    path = configs.save_dir
    path = os.path.join(path, 'output')
    path = os.path.join(path, DATASET_KEYS[params.source_dataset])

    pretrain_specifiers = []
    pretrain_specifiers.append(BACKBONE_KEYS[params.backbone])
    pretrain_specifiers.append(MODEL_KEYS[params.model])
    if previous_step:
        if params.pls:
            pretrain_specifiers.append('LS')
        else:
            raise Exception('Should not fetch previous_step when params.pls is False')
    else:
        if params.pls:
            pretrain_specifiers.append('PLS')
        if params.ls:
            pretrain_specifiers.append('LS')
        if params.us:
            pretrain_specifiers.append('US')
        if params.ut:
            pretrain_specifiers.append('UT')
    pretrain_specifiers.append(params.tag)
    path = os.path.join(path, '_'.join(pretrain_specifiers))

    if params.target_dataset:
        path = os.path.join(path, DATASET_KEYS[params.target_dataset])

    if makedirs:
        os.makedirs(path, exist_ok=True)

    return path


def get_pretrain_state_path(output_directory, epoch=0):
    """
    :param output_directory:
    :param epoch: Number of completed epochs. I.e., 0 = initial.
    :return:
    """
    basename = 'pretrain_state_{:04d}.pt'.format(epoch)
    return os.path.join(output_directory, basename)


def get_final_pretrain_state_path(output_directory):
    glob_pattern = os.path.join(output_directory, 'pretrain_state_*.pt')
    paths = glob.glob(glob_pattern)

    pattern = re.compile('pretrain_state_(\d{4}).pt')
    paths_by_epoch = dict()
    for path in paths:
        match = pattern.search(path)
        if match:
            paths_by_epoch[match.group(1)] = path

    if len(paths_by_epoch) == 0:
        raise FileNotFoundError('Could not find valid pre-train state file in {}'.format(output_directory))

    max_epoch = max(paths_by_epoch.keys())
    return paths_by_epoch[max_epoch]


def get_pretrain_params_path(output_directory):
    return os.path.join(output_directory, 'pretrain_params.json')