from flask import jsonify, request, abort
from identity.model.id import PseudoRandomIdProvider
from .. import blueprint, db
from ..decorators import validate_json
from ..model import get_api_key


@blueprint.route('/create_pseudorandom_ids', methods=['POST'])
@validate_json({
    'type': 'object',
    'properties': {
        'prefix': {'type': 'string'},
        'id_count': { "type": "number", "multipleOf": 1.0, "minimum": 1 },
    },
    "required": ["prefix", "id_count"]
})
def create_pseudorandom_ids():
    id_provider = PseudoRandomIdProvider.query.filter_by(prefix=request.json.get('prefix')).first()

    if id_provider is None:
        abort(400)

    api_key = get_api_key(request)

    results = id_provider.allocate_ids(request.json.get('id_count'))

    barcodes = [r.barcode for r in results]

    db.session.commit()

    return jsonify({'ids': barcodes}), 201
