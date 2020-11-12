from utils import *
from ray import *
from cli import render

#textures
brown = Material(vec([0.5, 0.33, 0.163]))
grass = Material(load_image("textures/dirt_grass.png"))
tree_texture = Material(load_image("textures/trees-normal.png"))
roof_texture = Material(load_image("textures/roof_texture.png"))
cube_texture = Material(load_image("textures/wood_texture.png"))

(i1, p1, n1, t1) = read_obj(open("models/pyramid.obj"))
(i2, p2, n2, t2) = read_obj(open("models/cube.obj"))
(i3, p3, n3, t3) = read_obj(open("models/low-poly-tree-1.obj"))
roof = Mesh(i1, p1 + [[0, 1.0, 0]], n1, t1, roof_texture)
cube = Mesh(i2, 0.5*p2 + [[0, 0.5, 0]], None, None, cube_texture)
tree1 = Mesh(i3, 0.5*p3 + [[1.0, 0, 0]], n3, t3, tree_texture)
tree2 = Mesh(i3, 0.4*p3 + [[-1.0, 0, 0.3]], n3, t3, tree_texture)

scene = Scene([
    # Make a big sphere for the floor
    Sphere(vec([0,-60,0]), 60., grass),
] + [
    roof
] + [
    cube
] + [
    tree1
] + [
    tree2
],  vec([0.15, 0.25, 0.85]))

lights = [
    PointLight(vec([12,10,5]), vec([500,500,500])),
    AmbientLight(0.1),
]

camera = Camera(vec([3,1,5]), target=vec([0,1,0]), vfov=30, aspect=16/9)

render(camera, scene, lights)
