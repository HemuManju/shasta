import bpy

ops = bpy.ops
scene = bpy.context.scene
mesh = bpy.ops.mesh

# Delete default scene objects
ops.object.select_all()
ops.object.select_all()
ops.object.delete()

bpy.context.scene.render.engine = 'BLENDER_RENDER'

# Import the model from our Three scene
ops.import_scene.obj(filepath="map.obj")

# Join the obj file
scene = bpy.context.scene
obs = []
for ob in scene.objects:
    # whatever objects you want to join...
    if ob.type == 'MESH':
        obs.append(ob)
ctx = bpy.context.copy()
# one of the objects to join
ctx['active_object'] = obs[0]
ctx['selected_objects'] = obs
bpy.ops.object.join(ctx)

# Smake UV project
for obj in bpy.context.selected_objects:
    if obj.type == 'MESH':
        bpy.context.scene.objects.active = obj
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(stretch_to_bounds=0)
        bpy.ops.object.editmode_toggle()

# Set it to active and go into edit mode
ops.object.mode_set(mode='EDIT')

# Mesh cleanup step, since what's coming out of Three is mostly cubes laying side by side.
# Unwrap the mesh
bpy.ops.mesh.uv_texture_add()
mesh.select_all()
ops.uv.lightmap_pack(PREF_IMG_PX_SIZE=4096)

# Create a new image to bake the lighting in to
bpy.ops.image.new(name="AO Map", width=4096, height=4096, alpha=0)
image = bpy.data.images['AO Map']

# Bake the lightmap
bpy.ops.mesh.select_all(action='SELECT')
for area in bpy.data.screens['UV Editing'].areas:
    if area.type == 'IMAGE_EDITOR':
        area.spaces.active.image = image
bpy.context.scene.render.bake_type = 'TEXTURE'
bpy.ops.object.bake_image()

# Save the baked image
image.filepath_raw = "map.png"
image.file_format = "PNG"
image.save()

ops.object.mode_set(mode='OBJECT')
# Delete all the texture and apply from image
for ob in bpy.data.objects:
    if ob.type != 'MESH' or len(ob.material_slots) == 0:
        continue
    ob.select = True
    bpy.context.scene.objects.active = ob
    matslots = len(ob.material_slots)
    for i in range(0, matslots):
        bpy.context.object.active_material_index = i
        bpy.ops.object.material_slot_remove()

# Add new material
mat = bpy.data.materials['Material']
tex = bpy.data.textures.new("SomeName", 'IMAGE')
slot = mat.texture_slots.add()
slot.texture = tex

# Save the obj file
bpy.ops.export_scene.obj(filepath='map.obj')
