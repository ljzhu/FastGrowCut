/*==============================================================================

  Program: 3D Slicer

  Portions (c) Copyright Brigham and Women's Hospital (BWH) All Rights Reserved.

  See COPYRIGHT.txt
  or http://www.slicer.org/copyright/copyright.txt for details.

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

==============================================================================*/

// Qt includes
#include <QtPlugin>

// FastGrowCut Logic includes
#include <vtkSlicerFastGrowCutLogic.h>

// FastGrowCut includes
#include "qSlicerFastGrowCutModule.h"
#include "qSlicerFastGrowCutModuleWidget.h"

//-----------------------------------------------------------------------------
Q_EXPORT_PLUGIN2(qSlicerFastGrowCutModule, qSlicerFastGrowCutModule);

//-----------------------------------------------------------------------------
/// \ingroup Slicer_QtModules_ExtensionTemplate
class qSlicerFastGrowCutModulePrivate
{
public:
  qSlicerFastGrowCutModulePrivate();
};

//-----------------------------------------------------------------------------
// qSlicerFastGrowCutModulePrivate methods

//-----------------------------------------------------------------------------
qSlicerFastGrowCutModulePrivate
::qSlicerFastGrowCutModulePrivate()
{
}

//-----------------------------------------------------------------------------
// qSlicerFastGrowCutModule methods

//-----------------------------------------------------------------------------
qSlicerFastGrowCutModule
::qSlicerFastGrowCutModule(QObject* _parent)
  : Superclass(_parent)
  , d_ptr(new qSlicerFastGrowCutModulePrivate)
{
}

//-----------------------------------------------------------------------------
qSlicerFastGrowCutModule::~qSlicerFastGrowCutModule()
{
}

//-----------------------------------------------------------------------------
QString qSlicerFastGrowCutModule::helpText()const
{
  return "This is a loadable module bundled in an extension";
}

//-----------------------------------------------------------------------------
QString qSlicerFastGrowCutModule::acknowledgementText()const
{
  return "This work was was partially funded by NIH grant 3P41RR013218-12S1";
}

//-----------------------------------------------------------------------------
QStringList qSlicerFastGrowCutModule::contributors()const
{
  QStringList moduleContributors;
  moduleContributors << QString("Jean-Christophe Fillion-Robin (Kitware)");
  return moduleContributors;
}

//-----------------------------------------------------------------------------
QIcon qSlicerFastGrowCutModule::icon()const
{
  return QIcon(":/Icons/FastGrowCut.png");
}

//-----------------------------------------------------------------------------
QStringList qSlicerFastGrowCutModule::categories() const
{
  return QStringList() << "Examples";
}

//-----------------------------------------------------------------------------
QStringList qSlicerFastGrowCutModule::dependencies() const
{
  return QStringList();
}

//-----------------------------------------------------------------------------
void qSlicerFastGrowCutModule::setup()
{
  this->Superclass::setup();
}

//-----------------------------------------------------------------------------
qSlicerAbstractModuleRepresentation * qSlicerFastGrowCutModule
::createWidgetRepresentation()
{
  return new qSlicerFastGrowCutModuleWidget;
}

//-----------------------------------------------------------------------------
vtkMRMLAbstractLogic* qSlicerFastGrowCutModule::createLogic()
{
  return vtkSlicerFastGrowCutLogic::New();
}
