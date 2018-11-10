import math

def radians_to_degrees(angle):
    return angle * (180.0 / math.pi)

def get_heading(thisX, thisY, thatX, thatY):
    """
    From player position and target position
    return the heading that points to the target
    (the server provides the TurnToHeading method)

    Parameters
    ----------
    thisX : int
        Player X coordinate
    thisY : int 
        Player Y coordinate
    thatX : int
        Target X coordinate
    thatY : int
        Target X coordinate

    Returns
    -------
    int
        Heading

    """
    heading = math.atan2(y2-y1, x2-x1)
    heading = radians_to_degrees(heading)
    heading = (heading - 360) % 360
    return math.fabs(heading)

def is_turn_left(currentHeading, desiredHeading):
    diff = desiredHeading - currentHeading
    if (diff > 0):
        return (diff > 180)
    else:
        return (diff >= -180)

def get_distance(thisX, thisY, thatX, thatY):
    """
    From player position and target position
    return the distance to the target)

    Parameters
    ----------
    thisX : int
        Player X coordinate
    thisY : int 
        Player Y coordinate
    thatX : int
        Target X coordinate
    thatY : int
        Target X coordinate

    Returns
    -------
    float
        Distance

    """
    headingX = thatX - thisX
    headingY = thatY - thisY
    return math.sqrt(headingX * headingX + headingY * cheadingY)
