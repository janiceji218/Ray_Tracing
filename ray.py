import numpy as np

from utils import *

"""
Core implementation of the ray tracer.  This module contains the classes (Sphere, Mesh, etc.)
that define the contents of scenes, as well as classes (Ray, Hit) and functions (shade) used in 
the rendering algorithm, and the main entry point `render_image`.

In the documentation of these classes, we indicate the expected types of arguments with a
colon, and use the convention that just writing a tuple means that the expected type is a
NumPy array of that shape.  Implementations can assume these types are preconditions that
are met, and if they fail for other type inputs it's an error of the caller.  (This might 
not be the best way to handle such validation in industrial-strength code but we are adopting
this rule to keep things simple and efficient.)
"""


class Ray:

    def __init__(self, origin, direction, start=0., end=np.inf):
        """Create a ray with the given origin and direction.

        Parameters:
          origin : (3,) -- the start point of the ray, a 3D point
          direction : (3,) -- the direction of the ray, a 3D vector (not necessarily normalized)
          start, end : float -- the minimum and maximum t values for intersections
        """
        # Convert these vectors to double to help ensure intersection
        # computations will be done in double precision
        self.origin = np.array(origin, np.float64)
        self.direction = np.array(direction, np.float64)
        self.start = start
        self.end = end


class Material:


    def __init__(self, k_d, k_s=0., p=20., k_m=0., k_a=None):
        """Create a new material with the given parameters.

        Parameters:
          k_d : float, (3,) or (h,w,3) -- the diffuse coefficient
          k_s : float, (3,) or (h,w,3) -- the specular coefficient
          p : float or (h,w) -- the specular exponent
          k_m : float, (3,) or (h,w,3) -- the mirror reflection coefficient
          k_a : float, (3,) or (h,w,3) -- the ambient coefficient (defaults to match diffuse color)
        """
        # TODO A5 (Step2) implement this function
        # Check if each property is an array of shape (h, w, 3)
        # If so, then apply the property using the uv coordinates supplied by the geometry.
        self.k_d = k_d
        self.k_s = k_s
        self.p = p
        self.k_m = k_m
        self.k_a = k_a if k_a is not None else k_d

    def lookup(self, t, hit):
        if (isinstance(t, float) or t.shape == (3,)):
            return t
        else:
            i = int(np.floor(hit.uv[0] * t.shape[1]))
            j = int(np.floor(hit.uv[1] * t.shape[0]))
            i_pixel = np.maximum(0, np.minimum(t.shape[1] - 1, i))
            j_pixel = np.maximum(0, np.minimum(t.shape[0] - 1, j))
#             print(i_pixel)
#             print(j_pixel)
            return t[j_pixel][i_pixel]

class Hit:

    def __init__(self, t, point=None, normal=None, uv=None, material=None):
        """Create a Hit with the given data.

        Parameters:
          t : float -- the t value of the intersection along the ray
          point : (3,) -- the 3D point where the intersection happens
          normal : (3,) -- the 3D outward-facing unit normal to the surface at the hit point
          uv : (2,) -- the texture coordinates at the intersection point
          material : (Material) -- the material of the surface
        """
        self.t = t
        self.point = point
        self.normal = normal
        self.uv = uv
        self.material = material

# Value to represent absence of an intersection
no_hit = Hit(np.inf)

class Sphere:

    def __init__(self, center, radius, material):
        """Create a sphere with the given center and radius.

        Parameters:
          center : (3,) -- a 3D point specifying the sphere's center
          radius : float -- a Python float specifying the sphere's radius
          material : Material -- the material of the surface
        """
        self.center = center
        self.radius = radius
        self.material = material

    def intersect(self, ray):
        """Computes the first (smallest t) intersection between a ray and this sphere.

        Parameters:
          ray : Ray -- the ray to intersect with the sphere
        Return:
          Hit -- the hit data
        """
        # TODO A5 (Step1) implement this function
        # Copy your implementation from A4
        # Then calculate uv coordinates, to be passed into the Hit initializer
        D = ray.direction
        E = ray.origin
        C = self.center
        R = self.radius
        B = 2*np.dot(D, E-C)
        A = np.dot(D, D)
        min_t = ray.start
        max_t = ray.end

        discriminant = B ** 2 - 4 * A * (np.dot(E-C, E-C)-R**2)

        if discriminant < 0:
            return no_hit

        t0 = (-1*B - np.sqrt(discriminant)) / (2*A)
        t1 = (-1*B + np.sqrt(discriminant)) / (2*A)

        if (t0 >= min_t and t0 <= max_t and t0 <= t1):
            t = t0
        elif (t1 >= min_t and t1 <= max_t):
            t = t1
        else:
            return no_hit

        P = E + t * D
        unit_normal = (P - C) / R
        normal = normalize(P - C)
        d_hat = normalize(P - C)
        u = 0.5 + (np.arctan2(d_hat[0], d_hat[2])) / (2 * np.pi)
        v = 0.5 + (np.arcsin(d_hat[1])) / np.pi

        return Hit(t, P, unit_normal, vec([u,v]), self.material)


class Triangle:

    def __init__(self, vs, material):
        """Create a triangle from the given vertices.

        Parameters:
          vs (3,3) -- an arry of 3 3D points that are the vertices (CCW order)
          material : Material -- the material of the surface
        """
        self.vs = vs
        self.material = material

    def intersect(self, ray):
        """Computes the intersection between a ray and this triangle, if it exists.

        Parameters:
          ray : Ray -- the ray to intersect with the triangle
        Return:
          Hit -- the hit data
        """
        # TODO A5 (Step1) implement this function
        # Copy your implementation from A4
        # Then calculate uv coordinates, to be passed into the Hit initializer
        vs = self.vs

        a = vs[0][0] - vs[1][0]
        b = vs[0][1] - vs[1][1]
        c = vs[0][2] - vs[1][2]
        d = vs[0][0] - vs[2][0]
        e = vs[0][1] - vs[2][1]
        f = vs[0][2] - vs[2][2]

        ray_dir = ray.direction
        ray_orig = ray.origin

        g = ray_dir[0]
        h = ray_dir[1]
        i = ray_dir[2]
        j = vs[0][0] - ray_orig[0]
        k = vs[0][1] - ray_orig[1]
        l = vs[0][2] - ray_orig[2]

        M = a * (e * i - h * f) + b * (g * f - d * i) + c * (d * h - e * g)

        t = -(f * (a * k - j * b) + e * (j * c - a * l) + d *
              (b * l - k * c)) / M

        if (t < ray.start or t > ray.end):
            return no_hit

        gamma = (i * (a * k - j * b) + h * (j * c - a * l) + g *
                 (b * l - k * c)) / M

        if (gamma < 0 or gamma > 1):
            return no_hit

        beta = (j * (e * i - h * f) + k * (g * f - d * i) +
                l * (d * h - e * g)) / M

        if (beta < 0 or beta > 1 - gamma):
            return no_hit

        P = ray_orig + t * ray_dir

        unit_normal = normalize(np.cross(vs[0] - vs[2], vs[1] - vs[2]))

        A = np.linalg.norm(np.cross(vs[1] - vs[0],vs[2] - vs[0])) / 2
        areaA = np.linalg.norm(np.cross(vs[1] - P,vs[2] - P)) / 2
        areaB = np.linalg.norm(np.cross(vs[0] - P,vs[2] - P)) / 2
        areaC = np.linalg.norm(np.cross(vs[0] - P,vs[1] - P)) / 2
        u = areaB / A
        v = areaC / A
        return Hit(t, P, unit_normal, vec([u, v]), self.material)



class Mesh:

    def __init__(self, inds, posns, normals, uvs, material):
        self.inds = np.array(inds, np.int32)
        self.posns = np.array(posns, np.float32)
        self.normals = np.array(normals, np.float32) if normals is not None else None
        self.uvs = np.array(uvs, np.float32) if uvs is not None else None
        self.material = material

    def intersect(self, ray):
        """Computes the intersection between a ray and this mesh, if it exists.
           Use the batch_intersect function in the utils package

        Parameters:
          ray : Ray -- the ray to intersect with the mesh
        Return:
          Hit -- the hit data
        """
        # TODO A5 (Step3 and Step4) implement this function
        # For step 4, check if uvs and normals are not None (respectively) 
        # If so, then interpolate them

        return no_hit


class Camera:

    def __init__(self, eye=vec([0,0,0]), target=vec([0,0,-1]), up=vec([0,1,0]), 
                 vfov=90.0, aspect=1.0):
        """Create a camera with given viewing parameters.

        Parameters:
          eye : (3,) -- the camera's location, aka viewpoint (a 3D point)
          target : (3,) -- where the camera is looking: a 3D point that appears centered in the view
          up : (3,) -- the camera's orientation: a 3D vector that appears straight up in the view
          vfov : float -- the full vertical field of view in degrees
          aspect : float -- the aspect ratio of the camera's view (ratio of width to height)
        """
        self.eye = eye
        self.aspect = aspect
        # TODO A5 copy implementation from A4
        self.target = target
        self.vfov = np.radians(vfov)
        self.w = normalize(eye - target)
        self.u = normalize(np.cross(up, self.w))
        self.v = np.cross(self.w, self.u)

    def generate_ray(self, img_point):
        """Compute the ray corresponding to a point in the image.

        Parameters:
          img_point : (2,) -- a 2D point in [0,1] x [0,1], where (0,0) is the lower left 
                      corner of the image and (1,1) is the upper right
        Return:
          Ray -- The ray corresponding to that image location (not necessarily normalized)
        """
        # TODO A5 copy your implementation from A4
        i = img_point[0]
        j = img_point[1]
        dist_vector = self.target - self.eye
        proj_dist = np.linalg.norm(dist_vector)
        height = 2 * proj_dist * np.tan(self.vfov / 2.0)
        width = self.aspect * height
        left = (-1) * width / 2.0
        bottom = (-1) * height / 2.0
        u = i * width + left
        v = j * height + bottom
        ray_origin = self.eye
        ray_direction = ((-1) * proj_dist * self.w) + u * self.u + v * self.v
        return Ray(ray_origin, ray_direction)


class PointLight:

    def __init__(self, position, intensity):
        """Create a point light at given position and with given intensity

        Parameters:
          position : (3,) -- 3D point giving the light source location in scene
          intensity : (3,) or float -- RGB or scalar intensity of the source
        """
        self.position = position
        self.intensity = intensity

    def illuminate(self, ray, hit, scene):
        """Compute the shading at a surface point due to this light.

        Parameters:
          ray : Ray -- the ray that hit the surface
          hit : Hit -- the hit data
          scene : Scene -- the scene, for shadow rays
        Return:
          (3,) -- the light reflected from the surface
        """
        # TODO A5 copy implementation from A4 and modify
        # material parameters need to be looked up by the uv's at the intersection point
        l = self.position - hit.point
        epsilon = 0.000001
        point = hit.point + l*epsilon
        shadow_ray = Ray(point, l, epsilon, 1)

        if (scene.intersect(shadow_ray).t > 1):

            # diffuse shading
            intensity = self.intensity
            position = self.position
            normal = hit.normal
            dist_to_source = np.linalg.norm(hit.point - position)
            diffuse_coeff = hit.material.lookup(hit.material.k_d, hit)
            v = (-1) * normalize(ray.direction)
            light_ray = normalize(position - hit.point)
            specular_coeff = hit.material.lookup(hit.material.k_s, hit)
            p = hit.material.lookup(hit.material.p, hit)

            # diffuse shading
            # diffuse_output = diffuse_coeff * (np.maximum(0, np.dot(normal, light_ray)) / (dist_to_source ** 2)) * intensity
            # specular shading
            shade_ray = Ray(hit.point, light_ray, epsilon)
            if (scene.intersect(shade_ray).t == np.inf):
                h = (v + light_ray) / np.linalg.norm(v + light_ray)
                specular_output = (diffuse_coeff + specular_coeff * ((np.dot(normal, h)) ** p)) * (
                    np.maximum(0, np.dot(normal, light_ray)) / (dist_to_source ** 2)) * intensity
                return specular_output

        return vec([0, 0, 0])


class AmbientLight:

    def __init__(self, intensity):
        """Create an ambient light of given intensity

        Parameters:
          intensity (3,) or float: the intensity of the ambient light
        """
        self.intensity = intensity

    def illuminate(self, ray, hit, scene):
        """Compute the shading at a surface point due to this light.

        Parameters:
          ray : Ray -- the ray that hit the surface
          hit : Hit -- the hit data
          scene : Scene -- the scene, for shadow rays
        Return:
          (3,) -- the light reflected from the surface
        """
        # TODO A5 copy implementation from A4 and modify
        # k_a needs to be looked up by the uv's at the intersection point
        intensity = self.intensity
        diffuse_coeff = hit.material.lookup(hit.material.k_a, hit)
        output = diffuse_coeff * intensity
        return output


class Scene:

    def __init__(self, surfs, bg_color=vec([0.2,0.3,0.5])):
        """Create a scene containing the given objects.

        Parameters:
          surfs : [Sphere, Triangle,  Mesh] -- list of the surfaces in the scene
          bg_color : (3,) -- RGB color that is seen where no objects appear
        """
        self.surfs = surfs
        self.bg_color = bg_color

    def intersect(self, ray):
        """Computes the first (smallest t) intersection between a ray and the scene.

        Parameters:
          ray : Ray -- the ray to intersect with the scene
        Return:
          Hit -- the hit data
        """
        # TODO A5 copy your implementation from A4
        surfaces = self.surfs

        min_t = np.inf
        i = no_hit

        for s in surfaces:
            intersect = s.intersect(ray)
            if (intersect.t < min_t):
                min_t = intersect.t
                i = intersect
        return i



MAX_DEPTH = 4

def shade(ray, hit, scene, lights, depth=0):
    """Compute shading for a ray-surface intersection.

    Parameters:
      ray : Ray -- the ray that hit the surface
      hit : Hit -- the hit data
      scene : Scene -- the scene
      lights : [PointLight or AmbientLight] -- the lights
      depth : int -- the recursion depth so far
    Return:
      (3,) -- the color seen along this ray
    When mirror reflection is being computed, recursion will only proceed to a depth
    of MAX_DEPTH, with zero contribution beyond that depth.
    """
    # TODO A5 copy implementation from A4 and modify
    # k_m needs to be looked up by the uv's at the intersection point
    bg_color = scene.bg_color

    if (hit.t < np.inf):
#        output = vec([hit.uv[0], hit.uv[1], 0])
        output = vec([0, 0, 0])
        k_m = hit.material.lookup(hit.material.k_m, hit)
        if (depth < MAX_DEPTH):
            normal = hit.normal
            r_dir = ray.direction
            normal = hit.normal
            m_dir = r_dir - 2 * np.dot(r_dir, normal) * normal
            m_ray = Ray(hit.point, m_dir, 0.0000001, np.inf)
            m_hit = scene.intersect(m_ray)

            if (m_hit != no_hit):
                output = output + k_m * \
                    shade(m_ray, m_hit, scene, lights, depth + 1)
            else:
                output = output + k_m * bg_color

        for light in lights:
            output = output + light.illuminate(ray, hit, scene)

        return output

    else:
        return bg_color


def render_image(camera, scene, lights, nx, ny):
    """Render a ray traced image.

    Parameters:
      camera : Camera -- the camera defining the view
      scene : Scene -- the scene to be rendered
      lights : Lights -- the lights illuminating the scene
      nx, ny : int -- the dimensions of the rendered image
    Returns:
      (ny, nx, 3) float32 -- the RGB image
    """
    # TODO A5 copy implementation from A4
    img = np.zeros((ny, nx, 3), np.float32)

    for x in range(0, nx):
        for y in range(0, ny):
            u = (x + 0.5) / nx
            v = (y + 0.5) / ny
            ray = camera.generate_ray((u, v))
            hit = scene.intersect(ray)
            img[y][x] = shade(ray, hit, scene, lights)

    return img

