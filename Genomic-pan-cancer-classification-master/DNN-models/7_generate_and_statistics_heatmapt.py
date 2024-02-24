# -*- encoding: utf-8 -*-
'''
@File    :   7_generate_and_statistics_heatmapt.py
@Time    :   2020/05/09 17:24:38
@Author  :   yetaoyu 
@Version :   1.0
@Contact :   taoyuye@gmail.com
@Desc    :   Generate a heatmap for each cancer heatmap samples 
			and statistics the genes corresponding to the importance score (pixel value) of the heatmap

			need "/ChromosomeGene/All/" and "geneNameCancer" folder generated by Generate-all-mutation-map project
'''

# here put the import lib
import numpy as np
import pandas as pd
import sys 
import glob
import datetime
import cv2

import matplotlib
matplotlib.use('TkAgg') # backend
import matplotlib.pyplot as plt
from skimage import io
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "6"
from os import scandir
from sklearn import preprocessing
 
# Generate a heatmap for each cancer heatmap samples and 
# statistics the genes corresponding to the importance score (pixel value) of the heatmap
def generate_heamap(path, gene_matrix_dict, gene_path, threshold_path, cancer_name):
	os.chdir(path)
	img_shape=(310,310,3)
	
	cancer_img = np.zeros((310,310), np.float64) 
	data = [] 
	cancer_genes = []
	cancer_genes_set = []

	# Read a list of cancer-related gene names
	cancer_genename_list = list()
	with open(gene_path + cancer_name + '_gene_name.txt', 'r') as mf:
		for line in mf:
			line = line.strip()
			cols = line.split()
			cancer_genename_list.append(cols[0])
	print("len(cancer_genename_list)=", len(cancer_genename_list))

	for img_file in scandir(path):
		# print("sample_path=", img_file.path)
		image = cv2.imread(img_file.path, 1)
		image = cv2.resize(image, (img_shape[1], img_shape[0])) # (width, height)
		img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		data.append(img)
	data = np.array(data)
	print("data.shape=", data.shape)

	for i in range(data.shape[1]):
		for j in range(data.shape[2]):
			temp = [data[k][i][j] for k in range(data.shape[0])]
			cancer_img[i][j] = np.mean(temp)
	cv2.imwrite(threshold_path + cancer_name + '.png', cancer_img)
	print("cancer_img.sort=", cancer_img.flatten()[cancer_img.flatten().argsort()[::-1]])
	print("cancer_img.count255=", list(cancer_img.flatten()).count(255))

	im = cv2.imread(threshold_path + cancer_name + '.png', cv2.IMREAD_GRAYSCALE)

	# Min-Max normalization
	tmp = im - im.min()
	tmp_2 = tmp/tmp.max()
	tmp_3 = np.uint8(tmp_2 * 255.0)
	print("tmp_3.count255=", list(tmp_3.flatten()).count(255))
	print("im.sort=", im.flatten()[im.flatten().argsort()[::-1]])

	# plt.subplot(1,2,1), plt.imshow(im, cmap='gray'), plt.title('mean'), plt.xticks([]), plt.yticks([]),plt.axis('off')
	# plt.subplot(1,2,2), plt.imshow(tmp_3, cmap='gray'), plt.title('normalization'), plt.xticks([]), plt.yticks([]),plt.axis('off')
	# plt.show()

	tmp_4 = tmp_3.flatten()
	tmp_5 = tmp_4.argsort()[::-1] # Values in descending order: tmp_4[tmp_5]

	print("tmp_5.sort=",tmp_4[tmp_5][:30])

	fopen = open(threshold_path + cancer_name + '_' + "TopGene.txt", 'w') # save a list of top genes
	for k in range(310*310):
		index = np.unravel_index(tmp_5[k], tmp_3.shape) 

		i = index[0]
		j = index[1]
		# BRCA = 17689 genes
		if ((i,j) in gene_matrix_dict.keys()):
			if gene_matrix_dict[(i,j)] in cancer_genename_list:
				cancer_genes.append(gene_matrix_dict[(i,j)])

				if gene_matrix_dict[(i,j)] not in cancer_genes_set: # locate in the corresponding cancer
					# print(gene_matrix_dict[(i,j)])
					cancer_genes_set.append(gene_matrix_dict[(i,j)])
					fopen.write(str(tmp_3[i][j]) + '\t' + gene_matrix_dict[(i,j)] + '\n')
					if k <= 30:
						print(str(gene_matrix_dict[(i,j)]))
	fopen.close()
	print("len(cancer_genes_set)= ", len(cancer_genes_set))
	print("len(cancer_genes)= ", len(cancer_genes))

# Returns the index dictionary representation of the 310 * 310 gene matrix
# path：Chromosome file path；
def construct_gene_name_dict(path):
	os.chdir(path)
	genes = list()
	
	#### Sort genes in chromosomal order
	# Read "chorm01.txt"-"chormY.txt" a total of 24 kinds of chromosome files in order
	chromosome_directories = [name for name in os.listdir(".") if os.path.isfile(name)]
	chromosome_directories.sort()
	# print("chromosome_directories=",chromosome_directories)

	# Gene name list: Obtain a list of file names which stores the gene list of the corresponding chromosome
	gene_chrom_dict = {0: 'gene_chrom01_list',1: 'gene_chrom02_list',2: 'gene_chrom03_list',
	3: 'gene_chrom04_list',4: 'gene_chrom05_list',5: 'gene_chrom06_list',6: 'gene_chrom07_list',
	7: 'gene_chrom08_list',8: 'gene_chrom09_list',9: 'gene_chrom10_list',10: 'gene_chrom11_list',
	11: 'gene_chrom12_list',12: 'gene_chrom13_list',13: 'gene_chrom14_list',14: 'gene_chrom15_list',
	15: 'gene_chrom16_list',16: 'gene_chrom17_list',17: 'gene_chrom18_list',18: 'gene_chrom19_list',
	19: 'gene_chrom20_list',20: 'gene_chrom21_list',21: 'gene_chrom22_list',22: 'gene_chromX_list',23: 'gene_chromY_list'}

	# open each chrom file,0-23 chromosomes
	for chrom in range(len(chromosome_directories)):
		gene_name_list = list()
		with open(chromosome_directories[chrom]) as mf:
			for line in mf:
				line = line.strip()
				cols = line.split()
				gene_name_list.append(cols[0])
		gene_chrom_dict[chrom] = gene_name_list
		# print("gene_chrom_dict[",chrom,"]=",len(gene_chrom_dict[chrom]))
		# print("gene_chrom_dict[",chrom,"]=",gene_chrom_dict[chrom])
				
	# Gene name dictionary: build a gene dictionary for each chromosome，eg. gene_index_chrom01={'ACD':0}
	# It is used to locate the position of the gene in the chromosome.
	gene_index_dict = {0: 'gene_index_chrom01',1: 'gene_index_chrom02',2: 'gene_index_chrom03',
	3: 'gene_index_chrom04',4: 'gene_index_chrom05',5: 'gene_index_chrom06',6: 'gene_index_chrom07',
	7: 'gene_index_chrom08',8: 'gene_index_chrom09',9: 'gene_index_chrom10',10: 'gene_index_chrom11',
	11: 'gene_index_chrom12',12: 'gene_index_chrom13',13: 'gene_index_chrom14',14: 'gene_index_chrom15',
	15: 'gene_index_chrom16',16: 'gene_index_chrom17',17: 'gene_index_chrom18',18: 'gene_index_chrom19',
	19: 'gene_index_chrom20',20: 'gene_index_chrom21',21: 'gene_index_chrom22',22: 'gene_index_chromX',23: 'gene_index_chromY'}
	for chrom in range(len(chromosome_directories)):
		# print("chrom is ",chrom) # 0-23
		gene_dict = dict()
		gene_index = 0
		for gene in range(len(gene_chrom_dict[chrom])):
			gene_dict[gene_chrom_dict[chrom][gene]] = gene_index
			gene_index += 1
		gene_index_dict[chrom] = gene_dict # genename:geneindex

	# <gene_index_dict Dictionary inversion> Gene index dictionary: build a gene index dictionary for each chromosome，eg. gene_name_chrom01={0:'ACD'}
	gene_name_dict = {0: 'gene_name_chrom01',1: 'gene_name_chrom02',2: 'gene_name_chrom03',
	3: 'gene_name_chrom04',4: 'gene_name_chrom05',5: 'gene_name_chrom06',6: 'gene_name_chrom07',
	7: 'gene_name_chrom08',8: 'gene_name_chrom09',9: 'gene_name_chrom10',10: 'gene_name_chrom11',
	11: 'gene_name_chrom12',12: 'gene_name_chrom13',13: 'gene_name_chrom14',14: 'gene_name_chrom15',
	15: 'gene_name_chrom16',16: 'gene_name_chrom17',17: 'gene_name_chrom18',18: 'gene_name_chrom19',
	19: 'gene_name_chrom20',20: 'gene_name_chrom21',21: 'gene_name_chrom22',22: 'gene_name_chromX',23: 'gene_name_chromY'}

	for chrom in range(len(chromosome_directories)):
		gene_name_dict[chrom] = {v:k for k,v in gene_index_dict[chrom].items()}
	
	# print("gene_index_dict[23]=", gene_index_dict[23])
	# print("gene_name_dict[23]=", gene_name_dict[23])

	 # Construct dictionary markers of gene matrix: gene_matrix_dict
	i = j = 0 # line index:i,column index:j
	gene_matrix_dict = dict()
	for chrom in range(len(chromosome_directories)):
		geneNum = len(gene_chrom_dict[chrom])
		# print("geneNum=", geneNum)
		
		for k in range(geneNum):
			gene_matrix_dict[(i,j)] = gene_name_dict[chrom][k] # "Kth" gene of chromosome "chrom"
			gene_matrix_dict[(i,j+1)] = gene_name_dict[chrom][k]
			gene_matrix_dict[(i,j+2)] = gene_name_dict[chrom][k]

			if i < 309:
				i = i + 1
			else:
				i = i % 309
				j = j + 3
		i = 0
		j = j + 3
	return gene_matrix_dict

def main():
	data_path = os.getcwd()
	 
	data_chrom_path = data_path + "/ChromosomeGene/All/" # Chromosome file path
	gene_matrix_dict = construct_gene_name_dict(data_chrom_path) # the index dictionary representation of the 310 * 310 gene matrix
	# print("gene_matrix_dict=", gene_matrix_dict)
	os.chdir(data_path)

	heatmaps_path = data_path + "/Guided-GradCAM/"
	os.chdir(heatmaps_path)
	cancer_directories = [name for name in os.listdir(".") if os.path.isdir(name)]
	print("cancer_directories=", cancer_directories)
	os.chdir(data_path)

	# the gene name list of different cancer
	gene_name_cancer_path = data_path + '/geneNameCancer/'

	threshold_path = data_path + '/thresholdGeneStatistic/' 
	if not os.path.exists(threshold_path):
		os.makedirs(threshold_path)

	# eg. ACC，BLCA，……
	for cancer in range(len(cancer_directories)):
		cancer_name = cancer_directories[cancer]
		print("cancer_name=",cancer_name)

		heatmap_gene_path = os.path.join(heatmaps_path, cancer_name)
		print("heatmap_gene_path=",heatmap_gene_path)
	
		generate_heamap(heatmap_gene_path, gene_matrix_dict, gene_name_cancer_path, threshold_path, cancer_name)

		os.chdir(data_path)

if __name__ == "__main__":
	main()
