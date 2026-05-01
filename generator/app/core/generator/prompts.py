SPATIAL_ANALYSIS_PROMPT = """
Role:
You are an expert in spatial analysis and interior arrangement.

Task:
Please help me analyze the following description. The description includes the
description of the apartment (existing furniture, etc.) and the user instruction. Your
task is to carefully observe and identify the relationships between all pieces of
furniture and objects described. Specifically, you should:
1. Identify furniture and objects: Recognize all the furniture and objects present in
the description or come up with your own ideas of furniture if the description lacks
this information.
2. Describe spatial relationships: Clearly explain the spatial arrangement and
relationships between the items (e.g., which items are adjacent, aligned, in front of,
behind, on top of, under, or beside others).
3. Categorize placements: Distinguish whether furniture or objects are placed against
the wall, in the center of the room, or in any other notable position.

Format:
Describe spatial relationship in the form of a paragraph.

Requirement:
Here are some principles you must follow:
1. Your analysis should provide a comprehensive description that captures the overall
layout and the relationships between objects to give a clear understanding of the
scene's structure and design logic.
2. You should refer to the existing furniture by its name, e.g. Chair-A, Chair-B, or
Table-A.

Example:
Apartment: an empty apartment.
Instruction: Please generate a living room scene featuring a sofa placed against the
wall, with a small side table on one side of the sofa, holding a table lamp. A
rectangular coffee table is positioned in front of the sofa, with a vase of flowers and
a stack of books on its surface. On either side of the coffee table, include two
armchairs facing each other, creating a cozy seating arrangement. Additionally, place a
set of shelves against the adjacent wall, displaying a mix of books and decorative items
to add personality to the room. 

Answer: 
The sofa is aligned with one wall, acting as an anchor for the seating arrangement. The
side table with the table lamp is directly adjacent to the sofa, suggesting convenient
access for reading or lighting. The coffee table is centrally placed in front of the
sofa, maintaining alignment for easy reach from the seating arrangement. The vase of
flowers and the stack of books on the coffee table add both decorative and functional
elements to the scene. The two armchairs are positioned symmetrically, facing each other
across the coffee table, creating a balanced and intimate arrangement. The shelves
against an adjacent wall serve as a secondary focal point, offering a vertical storage
and display solution. They are likely perpendicular to the wall with the sofa for
practical accessibility and visual balance.
"""

SPATIAL_RELATIONSHIP_PROMPT = """
Role:
You are an experienced room designer.

Task:
Please help me analyze the following information and give output in the specified format.
Here is the current information:
Spatial relationship description: {0}
Here are the constraints and their definitions:
1. global constraint (The relationship between furniture and room):
1) floor: on floor: Indicates that the furniture is placed on the floor.
2) wall: 
flush wall: Used to constrain objects that are mounted on the wall.
against wall:An additional constraint to “onfloor"; specifies that furniture on the
floor is also placed against the wall.
far wall:An additional constraint to “onfloor"; specifies that furniture on the floor is
placed far from the wall.
3) ceiling: hanging: used to constrain furniture that is mounted on the ceiling.
2. side constraint (between furniture)
1) obj, in front of: This constraint specifies that one object is placed directly in
front of another. For example, a coffee table positioned in front of a sofa creates a
convenient and accessible surface for those seated.
2) obj, face to face:This involves two objects arranged facing each other, fostering
interaction and conversation. An example is two armchairs placed face to face across a
coffee table in a living room.
3) obj, back to back:This means two objects are placed with their backs against each
other, often to optimize space or define separate areas.
4) obj, side by side:Objects are placed next to each other along their sides, forming a
continuous line or larger unit. For example, two cabinets placed side by side create a
larger storage area in a dining room.
5) obj, left/right to: One object is placed to the left or right side of another,
indicating lateral positioning. For instance, a side table placed to the left of a bed
provides surface area for essentials, or a floor lamp positioned to the right of an
armchair offers optimal lighting for reading.
6) obj, aligned with:This involves placing objects symmetrically on both the left and
right sides of another object, creating balance and harmony. For example, two bedside
tables on either side of a bed, providing symmetry and convenient access to essentials
from both sides.
3. on constraint between furniture
obj, on top: Restrict objects to be placed on other items, such as on top of desk,
tvstand, coffeetable, island, diningtable, or cocktailtable.

Format:
The output format must be:object-x | global constraint | side constraint | on constraint
For example:
sofa-0 | on floor | against wall
coffee table-0 | on floor | sofa, in front of
armchair-0 | on floor | coffee table, face to face
side table-0 | on floor | bed, left/right to
floor lamp-0 | on floor | armchair, left/right to
cup-0 | coffee table, on top
cup-1 | coffee table, on top

Requirement:
Here are some principles you must follow:
1. For each object, there must be a global constraint or an on constraint, and there can
be a side constraint, but a side constraint is not required.
2. Situations where on constraint appears: This furniture cannot have global constraint
or side constraint.
3. Please follow the desired format *strictly* (do not add any additional text at the
beginning or end) to provide the constraints for each object. Place each constraint in
its own line.

Example:
Instruction:
Spatial relation description: The sofa is aligned with one wall, acting as an anchor for
the seating arrangement. The side table with the table lamp is directly adjacent to the
sofa, suggesting convenient access for reading or lighting. The coffee table is
centrally placed in front of the sofa, maintaining alignment for easy reach from the 
seating arrangement. The vase of flowers and the stack of books on the coffee table add
both decorative and functional elements to the scene. The two armchairs are positioned
symmetrically, facing each other across the coffee table, creating a balanced and
intimate arrangement. The shelves against an adjacent wall serve as a secondary focal
point, offering a vertical storage and display solution. They are likely perpendicular
to the wall with the sofa for practical accessibility and visual balance.
Answer:
sofa | on floor | against wall
side table | on floor | sofa, left/right to
lamp | side table, on top
coffee table | on floor | sofa, in front of 
vase | coffee table, on top
book stack | coffee table, on top
armchair-a | on floor | sofa, face to face
armchair-b | on floor | sofa, face to face
simple bookcase | on floor | against wall
"""

IDENTIFY_ACTIONS_PROMPT = """
Role:
You are an expert in spatial analysis and interior arrangement.

Task:
Please help me identify which furniture was or should be removed or moved according to
the provided instruction. You will be given a description of the apartment before the
change, user's instruction of how to change it, and the description of the apartment
after the change.

Format:
The output format must be:
removed: list of comma-separated furniture
moved: list of comma-separated furniture
For example:
removed: Stove-A, Chair-A
moved: Chair-B

Requirement:
Please follow the desired format *strictly* (do not add any additional text at the
beginning or end). You should refer to the existing furniture by its name, e.g.
Chair-A, Chair-B, or Table-A.

Example:
Apartment: Chair-A and Chair-B placed on the opposite sides of the Table-A.
Instruction: Move the furniture closer to the wall, remove one of the chairs.
Result: Chair-B is placed near the Table-A, which is placed against the wall.

Answer:
removed: Chair-A
moved: Chair-B, Table-A
"""

A = """
object | type | a brief but  description

Example:
Instruction:
Answer:
chair-a | 
"""
