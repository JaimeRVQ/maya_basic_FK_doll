# -*- coding: UTF-8 -*-
'''
Author: Jaime Rivera
File: basic_doll_FK.py
Date: 2018.11.17
Revision: 2018.11.17
Copyright: Copyright Jaime Rivera 2018 | www.jaimervq.com
           The program(s) herein may be used, modified and/or distributed in accordance with the terms and conditions
           stipulated in the Creative Commons license under which the program(s) have been registered. (CC BY-SA 4.0)

Brief: This executable file generates a full-body FK rigged model, in the shape of a wooden doll.

'''

__author__ = 'Jaime Rivera <jaime.rvq@gmail.com>'
__copyright__ = 'Copyright 2018, Jaime Rivera'
__credits__ = []
__license__ = 'Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)'
__maintainer__ = 'Jaime Rivera'
__email__ = 'jaime.rvq@gmail.com'
__status__ = 'Testing'

from maya import cmds

# Short names
l = 'left'
r = 'right'
c = 'center'


# -------------------------------- BODYPART CLASS -------------------------------- #

# Body part class
class BodyPart(object):

    def __init__(self, name, side, curve, geos=None):
        self.name = name + '_' + side
        self.driving_curve = curve
        self.geos = []
        if geos is not None:
            if isinstance(geos, str):
                self.geos.append(geos)
            elif isinstance(geos, list):
                self.geos = geos
        self.father = None
        self.childs = []

    def getName(self):
        return self.name

    def appendGeos(self, new_geo):
        if isinstance(new_geo, str) or isinstance(new_geo, unicode):
            self.geos.append(str(new_geo))
        elif isinstance(new_geo, list):
            self.geos.extend(new_geo)

    def getFatherName(self):
        if self.father is not None:
            return self.father.getName()

    def getChildsNames(self):
        return [child.getName() for child in self.childs]

    def defineFather(self, given_father):
        self.father = given_father
        given_father.recieveChild(self)

    def recieveChild(self, recieved_child):
        self.childs.append(recieved_child)

    def buildHierarchy(self):
        annulate_object(self.driving_curve)
        for geo in self.geos:
            annulate_object(geo)
            cmds.parent(geo, self.driving_curve)
        for child in self.childs:
            cmds.parent(child.driving_curve, self.driving_curve)
            child.buildHierarchy()

    def __str__(self):
        has_mirrored_version = ''
        if 'RIGHT' in self.name.upper() or 'LEFT' in self.name.upper():
            has_mirrored_version = ' (has a mirrored version)'
        return '\n{0}: Body part object{1}\n' \
               '-Driving curve: {2}\n' \
               '-Geometries driven: {3}\n' \
               '-Father body part: {4}\n' \
               '-Child body part(s): {5}'.format(self.name.upper(), has_mirrored_version, self.driving_curve, self.geos,
                                                 self.getFatherName(), self.getChildsNames())


# -------------------------------- BODYPART-RELATED FUNCTIONS -------------------------------- #

# Curve painting function
def paintCurve(current, side):
    if side == c:
        color = 22
    elif side == l:
        color = 13
    else:
        color = 6

    cmds.setAttr('{}.overrideEnabled'.format(current), 1)
    cmds.setAttr('{}.overrideColor'.format(current), color)


# Joint creation function
def create_joint(name, side, position):
    groove = True
    j_radius = 0.05
    rotation = [90, 90, 0]
    ctrl_rotation = [90, 0, 0]

    if name in ['elbow', 'knee', 'ankle', 'wrist']:
        j_radius = 0.038
        if name in ['wrist', 'ankle']:
            j_radius = 0.032
            if name == 'wrist':
                rotation = [90, 0, 0]
    elif name == 'shoulder':
        rotation = [90, 0, 0]
        ctrl_rotation = [45, 90, 0]
        if side == r:
            ctrl_rotation = [-45, 90, 0]
    elif name == 'neck':
        groove = False
    elif name == 'waist':
        j_radius = 0.08
        groove = False

    ctrl_crv = cmds.circle(name='{0}_joint_{1}_crv'.format(name, side), radius=1.75 * j_radius)

    cmds.move(position[0], position[1], position[2], ctrl_crv)
    cmds.rotate(ctrl_rotation[0], ctrl_rotation[1], ctrl_rotation[2], ctrl_crv)

    paintCurve(ctrl_crv[0], side)

    joint_geo = cmds.polySphere(name='{0}_joint_{1}_geo'.format(name, side), radius=j_radius, sy=21)

    cmds.move(position[0], position[1], position[2], joint_geo)
    cmds.rotate(rotation[0], rotation[1], rotation[2], joint_geo)

    if groove:
        cmds.polyExtrudeFacet('{0}_joint_{1}_geo.f[180:199]'.format(name, side), kft=True, ltz=-0.004)


# Curve/geo annulation
def annulate_object(target_object):

    cmds.makeIdentity(target_object, apply=True)

    cmds.delete(target_object, constructionHistory=True)

    target_properties = []

    if 'crv' in target_object:

        if ('root' not in target_object) and ('master' not in target_object):
            target_properties.extend(['{}.tx'.format(target_object), '{}.ty'.format(target_object), '{}.tz'.format(target_object)])
        target_properties.extend(['{}.sx'.format(target_object), '{}.sy'.format(target_object), '{}.sz'.format(target_object)])

    else:
        target_properties.extend(['{}.tx'.format(target_object), '{}.ty'.format(target_object), '{}.tz'.format(target_object)])
        target_properties.extend(['{}.rx'.format(target_object), '{}.ry'.format(target_object), '{}.rz'.format(target_object)])
        target_properties.extend(['{}.sx'.format(target_object), '{}.sy'.format(target_object), '{}.sz'.format(target_object)])

    for attr in target_properties:
        cmds.setAttr(attr, lock=True, keyable=False)


# -------------------------------- BODY PARTS CREATION -------------------------------- #

# MASTER CONTROL
# ----------------
main_group = cmds.group(name='BASIC_DOLL_FK', empty=True)

master_points = [(0.96, 0.0, 0.0), (0.917, 0.0, 0.024), (0.618, 0.0, 0.198), (0.575, 0.0, 0.223),
                 (0.575, 0.0, 0.209), (0.575, 0.0, 0.116), (0.575, 0.0, 0.102), (0.568, 0.0, 0.102),
                 (0.521, 0.0, 0.102), (0.514, 0.0, 0.102), (0.473, 0.0, 0.31), (0.31, 0.0, 0.473),
                 (0.102, 0.0, 0.514), (0.102, 0.0, 0.521), (0.102, 0.0, 0.568), (0.102, 0.0, 0.575),
                 (0.116, 0.0, 0.575), (0.209, 0.0, 0.575), (0.223, 0.0, 0.575), (0.198, 0.0, 0.618),
                 (0.024, 0.0, 0.917), (0.0, 0.0, 0.96), (-0.024, 0.0, 0.917), (-0.198, 0.0, 0.618),
                 (-0.223, 0.0, 0.575), (-0.209, 0.0, 0.575), (-0.116, 0.0, 0.575), (-0.102, 0.0, 0.575),
                 (-0.102, 0.0, 0.568), (-0.102, 0.0, 0.521), (-0.102, 0.0, 0.514), (-0.31, 0.0, 0.473),
                 (-0.473, 0.0, 0.31), (-0.514, 0.0, 0.102), (-0.521, 0.0, 0.102), (-0.568, 0.0, 0.102),
                 (-0.575, 0.0, 0.102), (-0.575, 0.0, 0.116), (-0.575, 0.0, 0.209), (-0.575, 0.0, 0.223),
                 (-0.618, 0.0, 0.198), (-0.917, 0.0, 0.024), (-0.96, 0.0, 0.0), (-0.917, 0.0, -0.024),
                 (-0.618, 0.0, -0.198), (-0.575, 0.0, -0.223), (-0.575, 0.0, -0.209), (-0.575, 0.0, -0.116),
                 (-0.575, 0.0, -0.102), (-0.568, 0.0, -0.102), (-0.521, 0.0, -0.102), (-0.514, 0.0, -0.102),
                 (-0.473, 0.0, -0.31), (-0.31, 0.0, -0.473), (-0.102, 0.0, -0.514), (-0.102, 0.0, -0.521),
                 (-0.102, 0.0, -0.568), (-0.102, 0.0, -0.575), (-0.116, 0.0, -0.575), (-0.209, 0.0, -0.575),
                 (-0.223, 0.0, -0.575), (-0.198, 0.0, -0.618), (-0.024, 0.0, -0.917), (0.0, 0.0, -0.96),
                 (0.024, 0.0, -0.917), (0.198, 0.0, -0.618), (0.223, 0.0, -0.575), (0.209, 0.0, -0.575),
                 (0.116, 0.0, -0.575), (0.102, 0.0, -0.575), (0.102, 0.0, -0.568), (0.102, 0.0, -0.521),
                 (0.102, 0.0, -0.514), (0.31, 0.0, -0.473), (0.473, 0.0, -0.31), (0.514, 0.0, -0.102),
                 (0.521, 0.0, -0.102), (0.568, 0.0, -0.102), (0.575, 0.0, -0.102), (0.575, 0.0, -0.116),
                 (0.575, 0.0, -0.209), (0.575, 0.0, -0.223), (0.618, 0.0, -0.198)]

master_crv = cmds.curve(name='master_crv', p=master_points)
cmds.closeCurve(ps=0, ch=0, rpo=1)

paintCurve('master_crv', c)

cmds.parent(master_crv, main_group)

master = BodyPart('master', c, 'master_crv')

# ROOT/HIP
# ----------------
root_crv = cmds.circle(name='root_center_crv', radius=0.18)
cmds.move(0, 1.102, 0)
cmds.rotate(90, 0, 0)
paintCurve('root_center_crv', c)

root_geo = cmds.polyCube(name='root_center_geo', sy=2, sx=2)
cmds.scale(0.154, 0.154, 0.122)
cmds.move(0, 1.093, 0)
cmds.polyMoveFacet('root_center_geo.f[10]', 'root_center_geo.f[11]', ty=-0.07)
cmds.polyMoveEdge('root_center_geo.e[30]', 'root_center_geo.e[31]', sx=1.35)
cmds.polyMoveEdge('root_center_geo.e[27]', 'root_center_geo.e[29]', sx=1.45)
cmds.polyMoveEdge('root_center_geo.e[16]', 'root_center_geo.e[13]', 'root_center_geo.e[22]', 'root_center_geo.e[25]', sz=1.25)

root = BodyPart('root', c, 'root_center_crv', 'root_center_geo')
root.defineFather(master)

# WAIST
# ----------------
create_joint('waist', c, [0, 1.201, 0])

chest_geo = cmds.polyCube(name='chest_center_geo', w=0.305, h=0.29, d=0.15, sy=2)
cmds.move(0, 1.389, 0)
cmds.polyMoveEdge('chest_center_geo.e[1]', 'chest_center_geo.e[4]', 'chest_center_geo.e[18:19]', ty=0.12)
cmds.polyMoveFacet('chest_center_geo.f[2]', 'chest_center_geo.f[5]', sx=0.6)
cmds.polyBevel('chest_center_geo.e[1]', 'chest_center_geo.e[4]', 'chest_center_geo.e[18:19]', o=0.027, sg=2)
cmds.polyBevel('chest_center_geo.e[0]', 'chest_center_geo.e[6]', 'chest_center_geo.e[3]', 'chest_center_geo.e[7]', o=0.027, sg=2)

waist = BodyPart('waist', c, 'waist_joint_center_crv', ['waist_joint_center_geo', 'chest_center_geo'])
waist.defineFather(root)

# LEFT ARM
# ----------------
# Shoulder_left
create_joint('shoulder', l, [0.187, 1.451, 0])
shoulder_left = BodyPart('shoulder', l, 'shoulder_joint_left_crv', 'shoulder_joint_left_geo')
shoulder_left.defineFather(waist)

# Arm_left
arm_left_geo = cmds.polyCylinder(name='arm_left_geo', r=0.04, h=0.27, sy=4)
cmds.move(0.189, 1.291, 0)
cmds.rotate(0, 0, 0.054)
cmds.polyMoveVertex('arm_left_geo.vtx[80:99]', sx=0.8, sz=0.8)
cmds.polyMoveVertex('arm_left_geo.vtx[0:19]', sx=0.7, sz=0.7)
shoulder_left.appendGeos(arm_left_geo[0])

# Elbow_left
create_joint('elbow', l, [0.190, 1.128, 0])
elbow_left = BodyPart('elbow', l, 'elbow_joint_left_crv', 'elbow_joint_left_geo')
elbow_left.defineFather(shoulder_left)

# Forearm_left
forearm_left_geo = cmds.polyCylinder(name='forearm_left_geo', r=0.037, h=0.265, sy=4)
cmds.move(0.195, 0.979, 0)
cmds.rotate(0, 0, 1.868)
cmds.polyMoveVertex('forearm_left_geo.vtx[80:99]', sx=0.8, sz=0.8)
cmds.polyMoveVertex('forearm_left_geo.vtx[0:19]', sx=0.7, sz=0.7)
elbow_left.appendGeos(forearm_left_geo[0])

# Wrist_left
create_joint('wrist', l, [0.200, 0.824, 0])
wrist_left = BodyPart('wrist', c, 'wrist_joint_left_crv', 'wrist_joint_left_geo')
wrist_left.defineFather(elbow_left)

# Hand_left
hand_left_geo = cmds.polyCube(name='hand_left_geo', w=0.042, h=0.15, d=0.1, sy=4)
cmds.move(0.223, 0.734)
cmds.rotate(0, 0, 14.441)
cmds.polyMoveFacet('hand_left_geo.f[4]', 'hand_left_geo.f[9]', sz=0.7)
cmds.polyMoveEdge('hand_left_geo.e[2]', tz=0.02)
cmds.move(0, 0.02, 0, 'hand_left_geo.e[1]', 'hand_left_geo.e[8]', os=True, wd=True, r=True)
wrist_left.appendGeos(hand_left_geo[0])

# ----------------


# RIGHT ARM
# ----------------
# Shoulder_right
create_joint('shoulder', r, [-0.187, 1.451, 0])
shoulder_right = BodyPart('shoulder', r, 'shoulder_joint_right_crv', 'shoulder_joint_right_geo')
shoulder_right.defineFather(waist)

# Arm_right
arm_right_geo = cmds.polyCylinder(name='arm_right_geo', r=0.04, h=0.27, sy=4)
cmds.move(-0.189, 1.291, 0)
cmds.rotate(0, 0, -0.054)
cmds.polyMoveVertex('arm_right_geo.vtx[80:99]', sx=0.8, sz=0.8)
cmds.polyMoveVertex('arm_right_geo.vtx[0:19]', sx=0.7, sz=0.7)
shoulder_right.appendGeos(arm_right_geo[0])

# Elbow_right
create_joint('elbow', r, [-0.190, 1.128, 0])
elbow_right = BodyPart('elbow', r, 'elbow_joint_right_crv', 'elbow_joint_right_geo')
elbow_right.defineFather(shoulder_right)

# Forearm_right
forearm_right_geo = cmds.polyCylinder(name='forearm_right_geo', r=0.037, h=0.265, sy=4)
cmds.move(-0.195, 0.979, 0)
cmds.rotate(0, 0, -1.868)
cmds.polyMoveVertex('forearm_right_geo.vtx[80:99]', sx=0.8, sz=0.8)
cmds.polyMoveVertex('forearm_right_geo.vtx[0:19]', sx=0.7, sz=0.7)
elbow_right.appendGeos(forearm_right_geo[0])

# Wrist_right
create_joint('wrist', r, [-0.200, 0.824, 0])
wrist_right = BodyPart('wrist', c, 'wrist_joint_right_crv', 'wrist_joint_right_geo')
wrist_right.defineFather(elbow_right)

# Hand_right
hand_right_geo = cmds.polyCube(name='hand_right_geo', w=0.042, h=0.15, d=0.1, sy=4)
cmds.move(-0.223, 0.734)
cmds.rotate(0, 0, -14.441)
cmds.polyMoveFacet('hand_right_geo.f[4]', 'hand_right_geo.f[9]', sz=0.7)
cmds.polyMoveEdge('hand_right_geo.e[2]', tz=0.02)
cmds.move(0, 0.02, 0, 'hand_right_geo.e[1]', 'hand_right_geo.e[8]', os=True, wd=True, r=True)
wrist_right.appendGeos(hand_right_geo[0])

# ----------------


# NECK
# ----------------
create_joint('neck', c, [0, 1.549, 0])
neck = BodyPart('neck', c, 'neck_joint_center_crv', 'neck_joint_center_geo')
neck.defineFather(waist)

# HEAD
# ----------------
head_crv = cmds.circle(name='head_center_crv', radius=0.12, )
cmds.move(0, 1.581, 0)
cmds.rotate(90, 0, 0)
paintCurve('head_center_crv', c)

head_geo = cmds.polySphere(name='head_center_geo', radius=0.095, )
cmds.move(0, 1.745, 0, head_geo)
cmds.polyMoveVertex('head_center_geo.vtx[0:179]', 'head_center_geo.vtx[380]', s=(1.0, 1.82, 1.0), ws=True)

head = BodyPart('head', c, 'head_center_crv', 'head_center_geo')
head.defineFather(neck)

# LEFT LEG
# ----------------
# Femoral_left
create_joint('femoral', l, [0.07, 0.911, 0])
femoral_left = BodyPart('femoral', l, 'femoral_joint_left_crv', 'femoral_joint_left_geo')
femoral_left.defineFather(root)

# Thigh_left
thigh_left_geo = cmds.polyCylinder(name='thigh_left_geo', r=0.06, h=0.355, sy=3)
cmds.move(0.07, 0.705, 0)
cmds.polyMoveVertex('thigh_left_geo.vtx[20:39]', sx=0.85, sz=0.85)
cmds.polyMoveVertex('thigh_left_geo.vtx[0:19]', sx=0.76, sz=0.76)
femoral_left.appendGeos(thigh_left_geo[0])

# Knee_left
create_joint('knee', l, [0.07, 0.503, 0])

knee_left = BodyPart('knee', l, 'knee_joint_left_crv', 'knee_joint_left_geo')

knee_left.defineFather(femoral_left)

# Tibia_left
tibia_left_geo = cmds.polyCylinder(name='tibia_left_geo', r=0.045, h=0.39, sy=3)
cmds.move(0.07, 0.287, 0)
cmds.polyMoveVertex('tibia_left_geo.vtx[20:39]', sx=0.75, sz=0.75)
cmds.polyMoveVertex('tibia_left_geo.vtx[0:19]', sx=0.55, sz=0.55)

knee_left.appendGeos(tibia_left_geo[0])

# Ankle_left
create_joint('ankle', l, [0.07, 0.076, 0])

ankle_left = BodyPart('ankle', l, 'ankle_joint_left_crv', 'ankle_joint_left_geo')

ankle_left.defineFather(knee_left)

# Foot_left
foot_left_geo = cmds.polyCube(name='foot_left_geo', w=0.08, h=0.07, d=0.2, sz=4)
cmds.move(0.07, 0.035, 0.05)
cmds.polyMoveEdge('foot_left_geo.e[1]', ty=-0.033)
cmds.polyMoveEdge('foot_left_geo.e[2]', ty=-0.0208)
cmds.polyMoveEdge('foot_left_geo.e[3]', ty=-0.0084)
cmds.polyMoveEdge('foot_left_geo.e[5]', ty=-0.0088)
cmds.polyMoveFacet('foot_left_geo.f[0]', sx=0.75)

ankle_left.appendGeos(foot_left_geo[0])

# ----------------


# RIGHT LEG
# ----------------
# Femoral_right
create_joint('femoral', r, [-0.07, 0.911, 0])

femoral_right = BodyPart('femoral', r, 'femoral_joint_right_crv', 'femoral_joint_right_geo')

femoral_right.defineFather(root)

# Thigh_right
thigh_right_geo = cmds.polyCylinder(name='thigh_right_geo', r=0.06, h=0.355, sy=3)
cmds.move(-0.07, 0.705, 0)
cmds.polyMoveVertex('thigh_right_geo.vtx[20:39]', sx=0.85, sz=0.85)
cmds.polyMoveVertex('thigh_right_geo.vtx[0:19]', sx=0.76, sz=0.76)
femoral_right.appendGeos(thigh_right_geo[0])

# Knee_right
create_joint('knee', r, [-0.07, 0.503, 0])
knee_right = BodyPart('knee', r, 'knee_joint_right_crv', 'knee_joint_right_geo')
knee_right.defineFather(femoral_right)

# Tibia_right
tibia_right_geo = cmds.polyCylinder(name='tibia_right_geo', r=0.045, h=0.39, sy=3)
cmds.move(-0.07, 0.287, 0)
cmds.polyMoveVertex('tibia_right_geo.vtx[20:39]', sx=0.75, sz=0.75)
cmds.polyMoveVertex('tibia_right_geo.vtx[0:19]', sx=0.55, sz=0.55)
knee_right.appendGeos(tibia_right_geo[0])

# Ankle_right
create_joint('ankle', r, [-0.07, 0.076, 0])
ankle_right = BodyPart('ankle', r, 'ankle_joint_right_crv', 'ankle_joint_right_geo')
ankle_right.defineFather(knee_right)

# Foot_right
foot_right_geo = cmds.polyCube(name='foot_right_geo', w=0.08, h=0.07, d=0.2, sz=4)
cmds.move(-0.07, 0.035, 0.05)
cmds.polyMoveEdge('foot_right_geo.e[1]', ty=-0.033)
cmds.polyMoveEdge('foot_right_geo.e[2]', ty=-0.0208)
cmds.polyMoveEdge('foot_right_geo.e[3]', ty=-0.0084)
cmds.polyMoveEdge('foot_right_geo.e[5]', ty=-0.0088)
cmds.polyMoveFacet('foot_right_geo.f[0]', sx=0.75)
ankle_right.appendGeos(foot_right_geo[0])


# -------------------------------- HIERARCHY BUILD -------------------------------- #

master.buildHierarchy()
cmds.select(d=True)


# -------------------------------- FEEDBACK -------------------------------- #

print '\nBody parts created:\n-------------------'
print master
print root
print waist
print shoulder_left
print elbow_left
print wrist_left
print shoulder_right
print elbow_right
print wrist_right
print neck
print head
print femoral_left
print knee_left
print ankle_left
print femoral_right
print knee_right
print ankle_right