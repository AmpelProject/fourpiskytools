from __future__ import absolute_import
from datetime import datetime
import uuid
import voeventparse as vp
from fourpiskytools.identity import id_keys


def generate_stream_id():
    """
    Get a string for use as a stream ID.

    The idea is to create a stream ID that is largely human-readable
    (hence the timestamp), but will not repeat if multiple packets are generated
    within a small timespan - so we append a uuid1() string.

    Note this results in quite a long string. If brevity is required, we
    could probably make do by using the first fragment of the uuid1 string,
    since the rest is a static function of the hostname, etc. But I see
    no compelling reason to risk UUID collisions by doing so.
    """
    datetime_format_short = '%y%m%d-%H%M.%S'
    timestamp = datetime.utcnow().strftime(datetime_format_short)
    stream_id = timestamp+'_'+str(uuid.uuid1())
    return stream_id


def create_skeleton_voevent(id, stream, role):
    v = vp.Voevent(stream=id[id_keys.address] + '/' + stream,
                   stream_id=generate_stream_id(), role=role)
    vp.set_who(v, date=datetime.utcnow(),
               author_ivorn=id[id_keys.address])
    vp.set_author(v,
                  shortName=id[id_keys.shortName],
                  contactName=id[id_keys.contactName],
                  contactEmail=id[id_keys.contactEmail],
                  )
    return v


def create_test_packet(id):
    v = create_skeleton_voevent(id, stream='TEST',
                                role=vp.definitions.roles.test)
    return v


def create_basic_location_alert(id, stream, role, description,
                                ra, dec, err,
                                event_time):
    """
    Create a skeleton VOEvent with a WhereWhen pointing at the given coords.

    Args:
        id (dict): Dictionary containing identity details,
            as defined in :mod:`fourpiskytools.identity`
        stream (string): Stream name, e.g. 'ProjectFooAlerts'
        role (string): 'observation', 'prediction','utility' or 'test'
        description (string): Description string inserted into 'What' section.
        ra (float): Right ascension (J2000 degrees)
        dec (float): Declination (J2000 degrees)
        err (float): Positional error-radius (degrees)
        event_time (datetime.datetime): Time of event (UTC).
    """

    v = create_skeleton_voevent(id, stream, role)
    v.What.Description = description
    vp.set_where_when(v,
          coords=vp.Position2D(ra=ra, dec=dec, err=err,
                               units='deg',
                               system=vp.definitions.sky_coord_system.fk5),
          obs_time=event_time,
          observatory_location=vp.definitions.observatory_location.geosurface)
    return v
