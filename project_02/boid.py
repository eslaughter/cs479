import bpy
import math
import mathutils
import random

# set up for importing python modules
import sys
import os
dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)
    
import boid_utils as utils

BOID_MATERIALS = [(1, .5, 0, 1), (1, 0, 0, 1), (1, 0.9, 0, 1), (1, 0, .28, 1)]
AVOIDANCE_DELAY = 5


# BOIDS
# ======================================================
class Boid(object):
    def __init__(self, flock_props, scene_objects, count, projection_points):
        self.flock_props = flock_props
        
        self.position = mathutils.Vector((
            random.uniform(-flock_props.x_range + 1, flock_props.x_range - 1),
            random.uniform(-flock_props.y_range + 1, flock_props.y_range - 1),
            random.uniform(-flock_props.z_range + 1, flock_props.z_range - 1 ),
        ))
        self.velocity = mathutils.Vector((
            random.uniform(-0.5, 0.5),
            random.uniform(-0.5, 0.5),
            random.uniform(-0.5, 0.5)
        ))
        self.acceleration  = mathutils.Vector((0, 0, 0))
        self.max_acceleration = flock_props.max_acceleration
        self.max_velocity = flock_props.max_velocity
        
        self.group = random.randint(0, flock_props.num_groups - 1)
        self.mat = bpy.data.materials.new(f"boid{count}_mat")
        self.mat.diffuse_color = BOID_MATERIALS[self.group]
        self.color = BOID_MATERIALS[self.group]

        self.object = utils.generate_boid_cone(self.mat, self.position, self.velocity)
        self.scene_objects = scene_objects
        
        self.projection_points = projection_points
        
        self.avoiding = False
        self.avoidance_delay = 0

    def edges(self):
        if self.position.x >= self.flock_props.x_range:
            self.position.x = -self.flock_props.x_range
        elif self.position.x <= -self.flock_props.x_range:
            self.position.x = self.flock_props.x_range
            
        if self.position.y >= self.flock_props.y_range:
            self.position.y = -self.flock_props.y_range
        elif self.position.y <= -self.flock_props.y_range:
            self.position.y = self.flock_props.y_range
            
        if self.position.z >= self.flock_props.z_range:
            self.position.z = -self.flock_props.z_range
        elif self.position.z <= -self.flock_props.z_range:
            self.position.z = self.flock_props.z_range
    
    def get_boids_in_perception(self, boids):
        perceived_boids = []
        for boid in boids:
            if boid is not self:
                if self.is_in_perception(boid):
                    perceived_boids.append(boid)
        return perceived_boids
    
    def is_in_perception(self, boid):
        within_perception_radius = utils.dist(self.position, boid.position) < self.flock_props.perception_radius
        
        boid_difference_angle = utils.angle_between_vectors(self.velocity, boid.position - self.position)
        
        within_perception_angle = math.degrees(boid_difference_angle) < self.flock_props.perception_angle
        within_group = self.group == boid.group
        return within_perception_radius and within_perception_angle and within_group
        
    def align(self, boids):
        steering = mathutils.Vector((0, 0, 0))
        total = 0
        for other in boids:
            steering = steering + other.velocity
            total += 1
        if total > 0:
            steering *= 1 / total
            steering = utils.set_mag(steering, self.max_velocity) 
            steering -= self.velocity
            steering = utils.limit(steering, self.max_acceleration)
        return steering
    
    def cohesion(self, boids):
        steering = mathutils.Vector((0, 0, 0))
        total = 0
        for other in boids:
            steering = steering + other.position
            total += 1
        if total > 0:
            steering *= 1 / total
            steering -= self.position
            steering = utils.set_mag(steering, self.max_velocity)
            steering -= self.velocity
            steering = utils.limit(steering, self.max_acceleration)
        return steering
            
    def separation(self, boids):
        steering = mathutils.Vector((0, 0, 0))
        total = 0
        for other in boids:
            d = utils.dist(self.position, other.position)
            diff = self.position - other.position
            diff *= 1 / d
            steering += diff
            total += 1
        if total > 0:
            steering *= 1 / total
            steering = utils.set_mag(steering, self.max_velocity)
            steering -= self.velocity
            steering = utils.limit(steering, self.max_acceleration)
        return steering
    
    def avoidance(self, boids, objects):
        steering = mathutils.Vector((0, 0, 0))
        obj = self.object
        min_dist = 100000000
        min_dist_obj = None
        for obj in self.scene_objects:
            mwi = obj.matrix_world.inverted()
            ray_begin = mwi @ self.position
            ray_end = mwi @ self.position + self.velocity
            ray_direction = (ray_end-ray_begin).normalized()
            result = obj.ray_cast(origin=ray_begin,direction=ray_direction, distance=self.flock_props.perception_radius)
            
            if result[0]:
                if utils.dist(self.object.location, result[2]) < min_dist:
                    min_dist = utils.dist(self.object.location, result[2])
                    min_dist_obj = obj
        if min_dist_obj:
            self.avoidance_delay = AVOIDANCE_DELAY
#            self.mat.diffuse_color = (0, 0, 1, 1)
            for point in self.projection_points:
                point.parent = self.object
                point_location = point.matrix_world.to_translation() - self.object.location
                point.parent = None
                mwi = min_dist_obj.matrix_world.inverted()
                ray_begin = mwi @ self.position
                ray_end = mwi @ self.position + point_location
                ray_direction = (ray_end-ray_begin).normalized()
                result = min_dist_obj.ray_cast(origin=ray_begin,direction=ray_direction, distance=self.flock_props.perception_radius)

                        
                if not result[0]:
                    steering = point_location
                    steering = utils.set_mag(steering, self.max_velocity)
                    steering -= self.velocity
                    steering = utils.limit(steering, self.max_acceleration)
                    return steering
#        else:
#            self.mat.diffuse_color = self.color
                
        return steering
    
                
            
    
            
        

    def flock(self, boids):
        perceived_boids = self.get_boids_in_perception(boids)
        alignment = self.align(perceived_boids)
        cohesion = self.cohesion(perceived_boids)
        separation = self.separation(perceived_boids)
        avoidance = self.avoidance(perceived_boids, self.scene_objects)
        
        alignment *= self.flock_props.alignment_strength
        cohesion *= self.flock_props.cohesion_strength
        separation *= self.flock_props.separation_strength
        
        total_mag = 0
        total_mag += avoidance.length
        self.acceleration += avoidance
        if self.avoidance_delay != 0:
            self.avoidance_delay -= 1
        else:
#        if avoidance.length != 0:
#            alignment *= 0.5
#            cohesion *= 0.5
#            separation *= 0.5
            if total_mag + separation.length > self.max_acceleration:
                self.acceleration += utils.set_mag(separation, self.max_acceleration - total_mag)
            else: 
                self.acceleration += separation
                if total_mag + cohesion.length > self.max_acceleration:
                    self.acceleration += utils.set_mag(cohesion, self.max_acceleration - total_mag)
                else:
                    self.acceleration += cohesion
                    if total_mag + alignment.length > self.max_acceleration:
                        self.acceleration += utils.set_mag(alignment, self.max_acceleration - total_mag)
                    else:
                        self.acceleration += alignment
        

        
    def update(self):
        self.position = self.position + self.velocity
        self.velocity = self.velocity + self.acceleration
        self.velocity = utils.limit(self.velocity, self.max_velocity)
        self.acceleration.zero()
    
    def show(self):
        self.object.location = self.position
        self.object.keyframe_insert(data_path="location", index=-1)
        
        self.mat.keyframe_insert(data_path="diffuse_color", index=-1)
        
        self.object.rotation_mode = 'QUATERNION'
        self.object.rotation_quaternion = self.velocity.to_track_quat('Z','Y')
        self.object.keyframe_insert(data_path="rotation_quaternion", index=-1)