#ifndef FRAMESAMPLE_H
#define FRAMESAMPLE_H
#include <blitz/array.h>

namespace Torch {
namespace machine {

/**
 * This class represents one Frame. It encapsulate a blitz::Array<float, 1>
 */
class FrameSample {
public:
  
  virtual ~FrameSample();

  /// Constructor
  FrameSample(const blitz::Array<float, 1>& array);
  
  /// Copy constructor
  FrameSample(const FrameSample& copy);

  /// Get the Frame
  const blitz::Array<float, 1>& getFrame() const; 
  
private:
  blitz::Array<float, 1> array;
};
}
}

#endif // FRAMESAMPLE_H