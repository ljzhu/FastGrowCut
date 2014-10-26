
#ifndef FASTGROWCUT_H
#define FASTGROWCUT_H

#include "vtkSlicerFastGrowCutModuleLogicExport.h"
#include "vtkImageData.h"
#include "FastGrowCutSegmenter.h"

#include <QProgressBar>
#include <QMainWindow>
#include <QStatusBar>
#include "qSlicerApplication.h"

const unsigned short SrcDimension = 3;
typedef float DistPixelType;											// float type pixel for cost function
typedef short SrcPixelType;
typedef unsigned char LabPixelType;

class VTK_SLICER_FASTGROWCUT_MODULE_LOGIC_EXPORT vtkFastGrowCutSeg : public vtkObject
{



public:
  static vtkFastGrowCutSeg* New();
  //vtkTypeRevisionMacro(vtkFastGrowCutSeg,vtkObject);
  //vtkTypeMacro(vtkKSlice,vtkObject);


  //set parameters of grow cut
  vtkSetObjectMacro(SourceVol, vtkImageData);
  vtkSetObjectMacro(SeedVol, vtkImageData);
  //vtkSetObjectMacro(OutputVol, vtkImageData);

  vtkSetMacro(InitializationFlag, bool);

  //processing functions
  void Initialization();
  void RunFGC();
  void PrintSelf(ostream &os, vtkIndent indent);

protected:
  vtkFastGrowCutSeg();
  virtual ~vtkFastGrowCutSeg();

private:
  //vtk image data (from slicer)
  vtkImageData* SourceVol;
  vtkImageData* SeedVol;

  std::vector<LabPixelType> m_imSeedVec;
  std::vector<LabPixelType> m_imLabVec;
  std::vector<SrcPixelType> m_imSrcVec;
  std::vector<long> m_imROI;

  //logic code
  FGC::FastGrowCut<SrcPixelType, LabPixelType> *m_fastGC;

  //state variables
  bool InitializationFlag;
};
#endif
