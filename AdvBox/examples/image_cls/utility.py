# Copyright (c) 2021 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
utility tools.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import distutils.util
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import os
import time

OUTPUT = './output/'
img_mean = np.array([0.485, 0.456, 0.406]).reshape((3, 1, 1))
img_std = np.array([0.229, 0.224, 0.225]).reshape((3, 1, 1))


def print_arguments(args):
    """Print argparse's arguments.
    Usage:
    .. code-block:: python
        parser = argparse.ArgumentParser()
        parser.add_argument("name", default="Jonh", type=str, help="User name.")
        args = parser.parse_args()
        print_arguments(args)
    :param args: Input argparse.Namespace for printing.
    :type args: argparse.Namespace
    """
    print("-----------  Configuration Arguments -----------")
    for arg, value in sorted(vars(args).items()):
        print("%s: %s" % (arg, value))
    print("------------------------------------------------")


def add_arguments(argname, type, default, help, argparser, **kwargs):
    """Add argparse's argument.
    Usage:
    .. code-block:: python
        parser = argparse.ArgumentParser()
        add_argument("name", str, "Jonh", "User name.", parser)
        args = parser.parse_args()
    """
    type = distutils.util.strtobool if type == bool else type
    argparser.add_argument(
        "--" + argname,
        default=default,
        type=type,
        help=help + ' Default: %(default)s.',
        **kwargs)


def check_output_directory(type):
    """
    create output directory
    Args:
         type: name of picture set for test
    """
    if not os.path.exists(OUTPUT):
        os.mkdir(OUTPUT, 0o755)
    if not os.path.exists(OUTPUT + "/" + type):
        os.mkdir(OUTPUT + "/" + type, 0o755)


def convert_net(img_example):
    """
    convert image array to original
    Args:
         img_example: array data of img
    """
    #reshape img_example
    output_img = np.reshape(img_example.astype('float32'), (3, 224, 224))

    output_img *= img_std
    output_img += img_mean
    output_img *= 255
    output_img = np.reshape(output_img.astype(np.uint8), (3, 224, 224))

    #convert C,H,W to H,W,C
    output_img = output_img.transpose((1, 2, 0))

    return output_img


def save_image(output_img, path):
    """
    save image from array that original or adversarial
    Args:
         img_example: array data of img
         path: directory and filename
    """
    im = Image.fromarray(output_img)
    im.save(path, 'png')


def generation_image(id, org_img, org_label, adv_img, adv_label, attack_method='FGSM'):
    """
    save image from array that original or adversarial
    imagenet data set
    Args:
         org_img: array data of test img
         adv_img: array data of adv img
         org_label: the inference label of test image
         adv_label: the adverarial label of adv image
         attack_method: the adverarial example generation method
    """
    DATA_TYPE = "imagenet"
    check_output_directory(DATA_TYPE)

    org_path= OUTPUT + DATA_TYPE + "/%d_original-%d-by-%s.png" \
              % (id, org_label, attack_method)
    adv_path= OUTPUT + DATA_TYPE + "/%d_adversary-%d-by-%s.png" \
              % (id, adv_label, attack_method)
    diff_path= OUTPUT + DATA_TYPE + "/%d_diff-x-by-%s.png" % (id, attack_method)

    org_output = convert_net(org_img)
    adv_output = convert_net(adv_img)
    diff_output = abs(adv_output - org_output)

    save_image(org_output, org_path)
    save_image(adv_output, adv_path)
    save_image(diff_output, diff_path)
    print("--------------------------------------------------")


def show_images_diff(original_img, original_label, adversarial_img, adversarial_label):
    """
    show original image, adversarial image and their difference
    Args:
        original_img: original image, numpy
        original_label:original label, int 
        adversarial_img: adversarial image
        adversarial_label: adversarial label

    Returns:

    """

    plt.figure()

    plt.subplot(131)
    plt.title('Original')
    plt.imshow(original_img)
    plt.axis('off')

    plt.subplot(132)
    plt.title('Adversarial')
    plt.imshow(adversarial_img)
    plt.axis('off')

    plt.subplot(133)
    plt.title('Adversarial-Original')
    difference = adversarial_img - original_img

    l0 = np.where(difference != 0)[0].shape[0]
    l2 = np.linalg.norm(difference)
    print("l0={} l2={}".format(l0, l2))

    #(-1,1)  -> (0,1)
    difference = difference / abs(difference).max() / 2.0 + 0.5
    plt.imshow(difference, cmap=plt.cm.gray)
    plt.axis('off')
    plt.tight_layout()
    ts = time.localtime(time.time())
    ts = time.strftime("%Y-%m-%d %H:%M:%S", ts)
    plt.savefig("output/orig_adv_diff_{}_{}.png".format(adversarial_label, ts))
    plt.show()


