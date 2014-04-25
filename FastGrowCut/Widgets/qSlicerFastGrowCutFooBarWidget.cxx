/*==============================================================================

  Program: 3D Slicer

  Copyright (c) Kitware Inc.

  See COPYRIGHT.txt
  or http://www.slicer.org/copyright/copyright.txt for details.

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

  This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
  and was partially funded by NIH grant 3P41RR013218-12S1

==============================================================================*/

// FooBar Widgets includes
#include "qSlicerFastGrowCutFooBarWidget.h"
#include "ui_qSlicerFastGrowCutFooBarWidget.h"

//-----------------------------------------------------------------------------
/// \ingroup Slicer_QtModules_FastGrowCut
class qSlicerFastGrowCutFooBarWidgetPrivate
  : public Ui_qSlicerFastGrowCutFooBarWidget
{
  Q_DECLARE_PUBLIC(qSlicerFastGrowCutFooBarWidget);
protected:
  qSlicerFastGrowCutFooBarWidget* const q_ptr;

public:
  qSlicerFastGrowCutFooBarWidgetPrivate(
    qSlicerFastGrowCutFooBarWidget& object);
  virtual void setupUi(qSlicerFastGrowCutFooBarWidget*);
};

// --------------------------------------------------------------------------
qSlicerFastGrowCutFooBarWidgetPrivate
::qSlicerFastGrowCutFooBarWidgetPrivate(
  qSlicerFastGrowCutFooBarWidget& object)
  : q_ptr(&object)
{
}

// --------------------------------------------------------------------------
void qSlicerFastGrowCutFooBarWidgetPrivate
::setupUi(qSlicerFastGrowCutFooBarWidget* widget)
{
  this->Ui_qSlicerFastGrowCutFooBarWidget::setupUi(widget);
}

//-----------------------------------------------------------------------------
// qSlicerFastGrowCutFooBarWidget methods

//-----------------------------------------------------------------------------
qSlicerFastGrowCutFooBarWidget
::qSlicerFastGrowCutFooBarWidget(QWidget* parentWidget)
  : Superclass( parentWidget )
  , d_ptr( new qSlicerFastGrowCutFooBarWidgetPrivate(*this) )
{
  Q_D(qSlicerFastGrowCutFooBarWidget);
  d->setupUi(this);
}

//-----------------------------------------------------------------------------
qSlicerFastGrowCutFooBarWidget
::~qSlicerFastGrowCutFooBarWidget()
{
}
