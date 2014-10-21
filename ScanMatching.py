import math
from decimal import *
from bigfloat import *
import numpy as np
import Ransac
import Trigo

L = 3
PI = math.pi

def dot((x1, y1), (x2, y2)):
  return x1 * x2 + y1 * y2

def vector((x1, y1), (x2, y2)):
  return (x2 - x1, y2 - y1)

def norma((x, y)):
  return math.hypot(x, y)

def radmod(angle):
  return math.fmod(2 * PI + math.fmod(angle, 2 * PI), 2 * PI)

def radmodBigFloat(angle):
  return (BigFloat(2 * PI) + (angle % BigFloat(2 * PI))) % BigFloat(2 * PI)

def isOnSegment(C, (A, B)):
  AC = vector(A, C)
  CB = vector(C, B)
  AB = vector(A, B)

  if (norma(AC) + norma(CB) == norma(AB)):
    return True
  else:
    return False

def getProjection((xa, ya), ((x1, y1), (x2, y2))):
  xu = x2 - x1
  yu = y2 - y1
  a, b = Ransac.findLineEq((x1, y1), (x2, y2))

  xh = (xa * xu - b * yu + ya * yu) / (xu + a * yu)
  yh = a * xh + b

  return (xh, yh)

def getMatchPointSegment((xa, ya), ((x1, y1), (x2, y2))):
  xh, yh = getProjection((xa, ya), ((x1, y1), (x2, y2)))

  if not isOnSegment((xh, yh), ((x1, y1), (x2, y2))):
    if norma(vector((xa, ya), (x1, y1))) < norma(vector((xa, ya), (x2, y2))):
      return (x1, y1)
    else:
      return (x2, y2)
  else:
    return (xh, yh)

def findMatchingPoint(point, ref):
  challenger  = getMatchPointSegment(point, (ref[0], ref[1]))
  dist        = norma(vector(point, challenger))

  for i in range(1, len(ref) - 1):
    tmp_challenger  = getMatchPointSegment(point, (ref[i], ref[i + 1]))
    tmp_dist        = norma(vector(point, tmp_challenger))

    if (tmp_dist < dist):
      challenger  = tmp_challenger
      dist        = tmp_dist

  return challenger

def matchPoints(ref, new, new2):
  result = []

  for i in range(len(new)):
    result.append((new2[i], findMatchingPoint(new[i], ref)))

  return result

def applyQ((xa, ya), (x, y, theta)):
  xa = xa + float(x)
  ya = ya + float(y)

  xa, ya = Trigo.cartToAng((xa, ya))
  ya     = radmod(ya + float(theta))

  return Trigo.angToCart((xa, ya))

def applyQList(points, (x, y, theta)):
  for i in range(len(points)):
    points[i] = applyQ(points[i], (x, y, theta))

def getA11(match):
  res = BigFloat(0)
  k = BigFloat(0)

  for i in range(len(match)):
    pix = BigFloat(match[i][1][0])
    piy = BigFloat(match[i][1][1])
    cix = BigFloat(match[i][0][0])
    ciy = BigFloat(match[i][0][1])
    ki  = pix ** 2 + piy ** 2 + L ** 2

    res = res + (1 - piy ** 2 / ki)

  return res

def getA12(match):
  res = BigFloat(0)
  k = BigFloat(0)

  for i in range(len(match)):
    pix = BigFloat(match[i][1][0])
    piy = BigFloat(match[i][1][1])
    cix = BigFloat(match[i][0][0])
    ciy = BigFloat(match[i][0][1])
    ki  = pix ** 2 + piy ** 2 + L ** 2

    res = res + (pix * piy / ki)

  return res

def getA13(match):
  res = BigFloat(0)
  k = BigFloat(0)

  for i in range(len(match)):
    pix = BigFloat(match[i][1][0])
    piy = BigFloat(match[i][1][1])
    cix = BigFloat(match[i][0][0])
    ciy = BigFloat(match[i][0][1])
    ki  = pix ** 2 + piy ** 2 + L ** 2

    res = res + (-ciy + (cix * pix + ciy * piy) * piy / ki)

  return res

def getA22(match):
  res = BigFloat(0)
  k = BigFloat(0)

  for i in range(len(match)):
    pix = BigFloat(match[i][1][0])
    piy = BigFloat(match[i][1][1])
    cix = BigFloat(match[i][0][0])
    ciy = BigFloat(match[i][0][1])
    ki  = pix ** 2 + piy ** 2 + L ** 2

    res = res + (1 - pix ** 2 / ki)

  return res

def getA23(match):
  res = BigFloat(0)
  k = BigFloat(0)

  for i in range(len(match)):
    pix = BigFloat(match[i][1][0])
    piy = BigFloat(match[i][1][1])
    cix = BigFloat(match[i][0][0])
    ciy = BigFloat(match[i][0][1])
    ki  = pix ** 2 + piy ** 2 + L ** 2

    res = res + (cix - (cix * pix + ciy * piy) * pix / ki)

  return res

def getA33(match):
  res = BigFloat(0)
  k = BigFloat(0)

  for i in range(len(match)):
    pix = BigFloat(match[i][1][0])
    piy = BigFloat(match[i][1][1])
    cix = BigFloat(match[i][0][0])
    ciy = BigFloat(match[i][0][1])
    ki  = pix ** 2 + piy ** 2 + L ** 2

    res = res + (cix ** 2 + ciy ** 2 - ((cix * pix + ciy * piy) ** 2) / ki)

  return res

def getB1(match):
  res = BigFloat(0)
  k = BigFloat(0)

  for i in range(len(match)):
    pix = BigFloat(match[i][1][0])
    piy = BigFloat(match[i][1][1])
    cix = BigFloat(match[i][0][0])
    ciy = BigFloat(match[i][0][1])
    ki  = pix ** 2 + piy ** 2 + L ** 2

    res = res + (cix - pix - (cix * piy - ciy * pix) * piy / ki)

  return res

def getB2(match):
  res = BigFloat(0)
  k = BigFloat(0)

  for i in range(len(match)):
    pix = BigFloat(match[i][1][0])
    piy = BigFloat(match[i][1][1])
    cix = BigFloat(match[i][0][0])
    ciy = BigFloat(match[i][0][1])
    ki  = pix ** 2 + piy ** 2 + L ** 2

    res = res + (ciy - piy - (cix * piy - ciy * pix) * pix / ki)

  return res

def getB3(match):
  res = BigFloat(0)
  k = BigFloat(0)

  for i in range(len(match)):
    pix = BigFloat(match[i][1][0])
    piy = BigFloat(match[i][1][1])
    cix = BigFloat(match[i][0][0])
    ciy = BigFloat(match[i][0][1])
    ki  = pix ** 2 + piy ** 2 + L ** 2

    res = res + (((cix * pix + cix * piy) / ki - 1) * (cix * piy - ciy * pix))

  return res

def getDeterminant(mat):
  a = mat[0][0]
  b = mat[0][1]
  c = mat[0][2]
  d = mat[1][0]
  e = mat[1][1]
  f = mat[1][2]
  g = mat[2][0]
  h = mat[2][1]
  i = mat[2][2]

  return a * e * i + b * f * g + c * d * h - c * e * g - f * h * a - i * b * d

def invertMatrix(mat):
  a = mat[0][0]
  b = mat[0][1]
  c = mat[0][2]
  d = mat[1][0]
  e = mat[1][1]
  f = mat[1][2]
  g = mat[2][0]
  h = mat[2][1]
  i = mat[2][2]

  array = np.array([[e * i - f * h, c * h - b * i, b * f - c * e],
                    [f * g - d * i, a * i - c * g, c * d - a * f],
                    [d * h - e * g, b * g - a * h, a * e - b * d]])

  return array / getDeterminant(mat)

def getA(match):
  return np.array([[getA11(match), getA12(match), getA13(match)],
                   [getA12(match), getA22(match), getA23(match)],
                   [getA13(match), getA23(match), getA33(match)]])

def getB(match):
  return np.array([[getB1(match)],
                   [getB2(match)],
                   [getB3(match)]])

def floatMatrixToBigFloat(mat):
  M = [[[BigFloat(0), BigFloat(0), BigFloat(0)] for i in range(len(mat[0]))] for j in range(len(mat))]

  for i in range(len(mat)):
    for j in range(len(mat[0])):
      M[i][j] = BigFloat(mat[i][j])

  return M

def getQmin(match):
  A = getA(match)
  B = getB(match)
  #A = np.linalg.matrix_power(A, -1)
  A = invertMatrix(A)
  A = -A
  A = floatMatrixToBigFloat(A)

  return np.dot(A, B)

def runScanMatching(ref, new, q):
  match = []
  tmp   = []
  qmin  = (BigFloat(q[0]), BigFloat(q[1]), BigFloat(q[2]))

  for i in range(100):
    tmp = list(new)
    applyQList(tmp, qmin)
    match = matchPoints(ref, tmp, new)
    qmin = getQmin(match)
    qmin[2] = radmodBigFloat(qmin[2])
    print qmin

  return qmin
