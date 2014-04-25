#ifndef utilities_hxx_
#define utilities_hxx_

// std
#include <iostream>
#include <fstream>
#include <limits>

// itk
#include "itkImage.h"
#include "itkImageFileReader.h"
#include "itkImageFileWriter.h"
#include "itkImportImageFilter.h"
//#include "itkVTKImageToImageFilter.h"
#include "itkImageRegionIteratorWithIndex.h"
#include "itkRegionOfInterestImageFilter.h"
#include "vtkImageData.h"

#include <csignal>

namespace FGC
{

	/*
	* createImage
	*/

	template<typename itkImageType>
	typename itkImageType::Pointer createImage(typename itkImageType::SizeType size, int iniValue) {

		typename itkImageType::Pointer img = itkImageType::New();
		typename itkImageType::SpacingType spacing;
		typename itkImageType::IndexType start;
		start.Fill(0);
		spacing.Fill(1);
		spacing[itkImageType::ImageDimension - 1] = 2;

		typename itkImageType::RegionType region;
		img->SetSpacing(spacing);
		region.SetSize(size);
		region.SetIndex(start);
		img->SetRegions(region);
		img->Allocate();
		img->FillBuffer(static_cast<typename itkImageType::PixelType>(iniValue));

		const typename itkImageType::SpacingType& sp = img->GetSpacing();
		std::cout << "Spacing = ";
		std::cout << sp[0] << ", " << sp[1] << std::endl;


		return img;

	}


template<typename PixelType>
void FindVTKImageROI(vtkImageData* im, std::vector<long>& imROI) {

    int* DIMS;
    long i,j,k,kk;
    bool foundLabel;

    DIMS = im->GetDimensions();
    foundLabel = false;
    imROI.resize(6);

    for(i = 0; i < DIMS[0]; i++)
        for(j = 0; j < DIMS[1]; j++)
            for(k = 0; k < DIMS[2]; k++) {
                if(*(static_cast<PixelType*>(im->GetScalarPointer(i,j,k))) != 0) {

                    if(!foundLabel) {
                        imROI[0] = i;  imROI[3] = i;
                        imROI[1] = j;  imROI[4] = j;
                        imROI[2] = k; imROI[5] = k;
                    }
                    else {
                        if(i < imROI[0]) imROI[0] = i;
                        if(i > imROI[3]) imROI[3] = i;
                        if(j < imROI[1]) imROI[1] = j;
                        if(j > imROI[4]) imROI[4] = j;
                        if(k < imROI[2]) imROI[2] = k;
                        if(k > imROI[5]) imROI[5] = k;
                    }
                    foundLabel = true;
                }
            }

    // Get Editor Radius information
    // TODO: get input from Editor
    int radius = 17;
    for(kk = 0; kk < 3; kk++) {
        if (imROI[kk] - radius >= 0) {
            imROI[kk] -= radius;
        }
        if(imROI[kk + 3] + radius < DIMS[kk]-1) {
            imROI[kk + 3] += radius;
        }
    }
}

template<typename PixelType>
void ExtractVTKImageROI(vtkImageData* im, const std::vector<long>& imROI, std::vector<PixelType>& imROIVec) {

    long i,j,k,index,DIMXYZ;

    DIMXYZ = (imROI[3] - imROI[0])*(imROI[4] - imROI[1])*(imROI[5] - imROI[2]);
    imROIVec.clear();
    imROIVec.resize(DIMXYZ);
    index = 0;
    for(k = imROI[2]; k < imROI[5]; k++)
        for(j = imROI[1]; j < imROI[4]; j++)
             for(i = imROI[0]; i < imROI[3]; i++){
               imROIVec[index++] = *(static_cast<PixelType*>(im->GetScalarPointer(i,j,k)));
            }
}

template<typename PixelType>
void UpdateVTKImageROI(const std::vector<PixelType>& imROIVec, const std::vector<long>& imROI,  vtkImageData* im) {

    // Set non-ROI as zeros
    memset((PixelType*)(im->GetScalarPointer()), 0, im->GetScalarSize()*im->GetNumberOfPoints());

    PixelType* pVal;
    long i,j,k, index;
    index = 0;
    for(k = imROI[2]; k < imROI[5]; k++)
        for(j = imROI[1]; j < imROI[4]; j++)
             for(i = imROI[0]; i < imROI[3]; i++){
                pVal = static_cast<PixelType*>(im->GetScalarPointer(i,j,k));
                *pVal = imROIVec[index++];
            }
}

template<typename ITKImageType>
void FindITKImageROI(typename ITKImageType::Pointer im, std::vector<long>& imROI) {

    typename ITKImageType::IndexType roiStart;
    typename ITKImageType::IndexType roiEnd;
    typename ITKImageType::IndexType start;
    typename ITKImageType::SizeType size;

    size = im->GetLargestPossibleRegion().GetSize();
    start = im->GetLargestPossibleRegion().GetIndex();


    roiStart[0] = 0; roiStart[1] = 0; roiStart[2] = 0;
    roiEnd[0] = 0; roiEnd[1] = 0; roiEnd[2] = 0;

    unsigned int ndims = im->GetImageDimension();

    bool foundLabel = false;
    itk::ImageRegionIteratorWithIndex< ITKImageType > label(im, im->GetBufferedRegion() );
    for(label.GoToBegin(); !label.IsAtEnd(); ++label) {
        if(label.Get() != 0) {
            typename ITKImageType::IndexType idx = label.GetIndex();
            for (unsigned i = 0; i < ndims; i++)  {
              if(!foundLabel)  {
                roiStart[i] = idx[i];
                roiEnd[i] = idx[i];
                }
              else
                {
                if(idx[i] <= roiStart[i])
                  {
                  roiStart[i] = idx[i];
                  }
                if(idx[i] >= roiEnd[i])
                  {
                  roiEnd[i] = idx[i];
                  }
                }
              }
          foundLabel = true;
          }
    }

    int radius = 17;
    for (unsigned i = 0; i < ndims; i++) {
      int diff = static_cast< int > (roiStart[i] - radius);
      if (diff >= start[i])  {
        roiStart[i] -= radius;
        }
      else  {
        roiStart[i] = start[i];
        }
      roiEnd[i] = (static_cast<unsigned int>(roiEnd[i] + radius) < size[i]) ? (roiEnd[i] + radius) : size[i]-1;

      }

    // copy ROI to vector
    imROI.resize(6);
    for(unsigned i = 0; i < 3; i++) {
        imROI[i] = roiStart[i];
        imROI[i + 3] = roiEnd[i];
    }
}

template<typename PixelType>
void ExtractITKImageROI(typename itk::Image<PixelType, 3>::Pointer  im, const std::vector<long>& imROI, \
                        std::vector<PixelType>& imROIVec) {

    // Copy itk image ROI to vector
    typedef itk::Image<PixelType, 3> ImageType;
    typename ImageType::IndexType index;
    long i,j,k,kk,DIMXYZ;

    DIMXYZ = (imROI[3] - imROI[0])*(imROI[4] - imROI[1])*(imROI[5] - imROI[2]);
    imROIVec.clear();
    imROIVec.resize(DIMXYZ);
    kk = 0;
    for(k = imROI[2]; k < imROI[5]; k++)
        for(j = imROI[1]; j < imROI[4]; j++)
            for(i = imROI[0]; i < imROI[3]; i++)  {
                index[0] = i; index[1] = j; index[2] = k;
                imROIVec[kk++] = im->GetPixel(index);
            }
}

template<typename PixelType>
void UpdateITKImageROI(const std::vector<PixelType>& imROIVec, const std::vector<long>& imROI,  \
                       typename itk::Image<PixelType, 3>::Pointer im) {

    typedef itk::Image<PixelType, 3> ImageType;
    typename ImageType::IndexType index;
    long i,j,k,kk;

    // Set non-ROI as zeros
    im->FillBuffer(0);
    kk = 0;
    for(k = imROI[2]; k < imROI[5]; k++)
        for(j = imROI[1]; j < imROI[4]; j++)
            for(i = imROI[0]; i < imROI[3]; i++)  {
            index[0] = i; index[1] = j; index[2] = k;
            im->SetPixel(index, imROIVec[kk++]);
        }
}




  /**
   * readImage
   */
  template< typename itkImage_t >
  typename itkImage_t::Pointer readImage(const char *fileName)
  {
    typedef itk::ImageFileReader< itkImage_t > ImageReaderType;
    typename ImageReaderType::Pointer reader = ImageReaderType::New();
    reader->SetFileName(fileName);

    typename itkImage_t::Pointer image;

    try
      {
        reader->Update();
        image = reader->GetOutput();
      }
    catch ( itk::ExceptionObject &err)
      {
        std::cerr<< "ExceptionObject caught !" << std::endl;
        std::cerr<< err << std::endl;
        raise(SIGABRT);
      }

    return image;
  }

  /**
   * writeImage
   */
  template< typename itkImage_t > void writeImage(typename itkImage_t::Pointer img, const char *fileName)
  {
    typedef itk::ImageFileWriter< itkImage_t > WriterType;

    typename WriterType::Pointer writer = WriterType::New();
    writer->SetFileName( fileName );
    writer->SetInput(img);
    writer->UseCompressionOn();

    try
      {
        writer->Update();
      }
    catch ( itk::ExceptionObject &err)
      {
        std::cout << "ExceptionObject caught !" << std::endl;
        std::cout << err << std::endl;
        raise(SIGABRT);
      }
  }

   template<typename VType>
    void WriteVectorIntoFile(const char* fnSave, const std::vector<VType>& vec) {

        try{
            std::ofstream outfile(fnSave);
            outfile.write((const char *)&vec[0], vec.size()*sizeof(VType));
        }
        catch ( itk::ExceptionObject &err)
          {
            std::cout << "Fail to write to file " << fnSave << std::endl;
            std::cout << err << std::endl;
            raise(SIGABRT);
          }
    }

    template<typename VType>
     void LoadVectorIntoFile(const char* fnLoad, std::vector<VType>& vec, const long VEC_SIZE) {

          try{
             std::ifstream infile(fnLoad);
              vec.resize(VEC_SIZE);
              infile.read((char *)&vec[0], vec.size()*sizeof(VType));
         }
         catch ( itk::ExceptionObject &err)
           {
             std::cout << "Fail to load file " << fnLoad << std::endl;
             std::cout << err << std::endl;
             raise(SIGABRT);
           }
     }
}// douher

#endif
