Vue.component('select2', {
  props: ['options', 'value'],
  mounted: function() {
    var vm = this;
    this.options.slice(0).unshift({id: '', text: 'Seleccione...'});
    $(this.$el).select2({data: this.options})
      .val(this.value)
      .trigger('change')
      .on('change', function() {
         vm.$emit('input', this.value)
      });
  },
  /**
   * Monitorea el valor de un select y carga los datos del select dependiente cuando este cambia su valor
   *
   * @author Ing. Roldan Vargas <rvargas@cenditel.gob.ve> | <roldandvg@gmail.com>
   * @type {Object}
   */
  watch: {
    value: function(value) {
      $(this.$el).val(value).trigger('change');
    },
    options: function(options) {
      try {
        options.slice(0).unshift({id: '', text: 'Seleccione...'});
        $(this.$el).empty().trigger('change').select2({data: options});
        //$(".select2").find('option').attr('data-toggle', 'tooltip');
      }
      catch(err) {}
    }
  },
  destroyed: function() {
    $(this.$el).off().select2('destroy');
  },
  template: `
  <select class="form-control select2" data-toggle="tooltip" title="Seleccione una opción">
    <slot></slot>
  </select>
  `
});

Vue.component('person', {
  props: {
    family_group_id: Number,
  },
  data() {
    return {
      record: {
        id: '',
        username: '',
        email: '',
        people: [],
      },
      vote_types: [],
      relationships: [],
      url: 'user/family-group/save',
      errors: {
        family_group: {
          username: [],
          email: [],
        },
        people: [{}],
      },
    }
  },

  created() {
    this.getVoteTypes();
    this.getRelationships();
  },

  methods: {
    /**
     * Método que permite reiniciar los datos del modelo record
     *
     * @author  William Páez <paez.william8@gmail.com>
     */
    reset() {
      this.record = {
        id: '',
        username: '',
        email: '',
        people: [],
      }
    },

    /**
     * Método que permite agregar personas dinamicamente
     *
     * @author  William Páez <paez.william8@gmail.com>
     */
    addPeople() {
      this.errors.people.push({
        first_name: '',
        last_name: '',
        has_id_number: 'y',
        id_number: '',
        email: '',
        phone: '',
        vote_type_id: '',
        relationship_id: '',
        family_head: false,
      });
      this.record.people.push({
        first_name: '',
        last_name: '',
        has_id_number: 'y',
        id_number: '',
        email: '',
        phone: '',
        vote_type_id: '',
        relationship_id: '',
        family_head: false,
      });
    },

    /**
     * Método que permite eliminar personas dinamicamente
     *
     * @author  William Páez <paez.william8@gmail.com>
     */
    deletePerson(index, el) {
      if( typeof(el[index].id) != 'undefined' ) {
        axios.get('/user/person/delete/' + el[index].id + '/').then(response => {
          console.log('Persona eliminada');
          el.splice(index, 1);
          this.errors.people.pop();
        });
      }
      else {
        el.splice(index, 1);
        this.errors.people.pop();
      }
    },

    /**
     * Método que obtiene los datos de un grupo familiar
     *
     * @author  William Páez <paez.william8@gmail.com>
     */
    getFamilyGroup() {
      axios.get('/user/family-group/detail/' + this.family_group_id + '/').then(response => {
        this.record = response.data.record;
        for (var index in this.record.people) {
          this.errors.people.push({
            first_name: '',
            last_name: '',
            has_id_number: 'y',
            id_number: '',
            email: '',
            phone: '',
            vote_type_id: '',
            relationship_id: '',
            family_head: false,
          });
        }
      });
    },
  },

  mounted() {
    if(this.family_group_id) {
      this.getFamilyGroup();
      this.url = 'user/family-group/update';
    }
  },

  template: `
  <div class="card">
    <div class="card-header">
      Registrar
    </div>
      <div class="card-body">
        <div class="row">
          <div class="col-xl-6 col-lg-6 col-md-6 col-sm-6">
            <div class="form-group">
              <label class="col-xl-5 col-lg-5 col-md-5 col-sm-5 control-label" for="id_username">
                Usuario: <i class="fa fa-asterisk item-required" aria-hidden="true"></i>
              </label>
              <div class="col-xl-7 col-lg-7 col-md-7 col-sm-7">
                <div class="form-inline">
                  <input type="text" class="form-control input-sm" data-toggle="tooltip" title="Indique el nombre de usuario" v-model="record.username">
                  <input type="hidden" v-model="record.id">
                </div>
              </div>
            </div>
            <div class="alert alert-danger" v-if="errors.family_group.username.length > 0">
              <ul>
                <li v-for="error in errors.family_group.username">{{ error }}</li>
              </ul>
            </div>
          </div>
          <div class="col-xl-6 col-lg-6 col-md-6 col-sm-6">
            <div class="form-group ">
              <label class="col-xl-5 col-lg-5 col-md-5 col-sm-5 control-label" for="id_email">
                Correo Electrónico: <i class="fa fa-asterisk item-required" aria-hidden="true"></i>
              </label>
              <div class="col-xl-7 col-lg-7 col-md-7 col-sm-7">
                <div class="form-inline">
                  <input type="email" class="form-control input-sm" data-toggle="tooltip" title="Indique el correo electrónico" v-model="record.email">
                </div>
              </div>
            </div>
            <div class="alert alert-danger" v-if="errors.family_group.email.length > 0">
              <ul>
                <li v-for="error in errors.family_group.email">{{ error }}</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <hr>
      <div class="card-body">
        <div v-if="errors.general_error">
          <div class="alert alert-danger" v-if="errors.general_error.length > 0">
            <ul>
              <li v-for="error in errors.general_error">{{ error }}</li>
            </ul>
          </div>
        </div>
        <div class="row">
          <div class="col-xl-6 col-lg-6 col-md-6 col-sm-6">
            <h6>
              Agregar Integrantes <i class="fa fa-plus-circle" @click="addPeople"></i>
            </h6>
          </div>
        </div>

        <div class="row" v-for="(person, index) in record.people">
          <div class="col-xl-3 col-lg-3 col-md-3 col-sm-3">
            <div class="form-group ">
              <input type="text" class="form-control input-sm" data-toggle="tooltip" title="Indique los nombres" placeholder="Nombres" v-model="person.first_name">
            </div>
            <div v-if="errors.people[index].first_name">
              <div class="alert alert-danger" v-if="errors.people[index].first_name.length > 0">
                <ul>
                  <li v-for="error in errors.people[index].first_name">{{ error }}</li>
                </ul>
              </div>
            </div>
          </div>
          <div class="col-xl-3 col-lg-3 col-md-3 col-sm-3">
            <div class="form-group ">
              <input type="text" class="form-control input-sm" data-toggle="tooltip" title="Indique los apellidos" placeholder="Apellidos" v-model="person.last_name">
            </div>
            <div v-if="errors.people[index].last_name">
              <div class="alert alert-danger" v-if="errors.people[index].last_name.length > 0">
                <ul>
                  <li v-for="error in errors.people[index].last_name">{{ error }}</li>
                </ul>
              </div>
            </div>
          </div>
          <div class="col-xl-4 col-lg-4 col-md-4 col-sm-4">
            <div class="form-inline">
              <div class="form-group">
                <select class="select2" title="¿Tiene cédula de identidad?" v-model="person.has_id_number">
                  <option value="y">Si</option>
                  <option value="n">No</option>
                </select>
              </div>
              <div class="form-group" v-show="person.has_id_number=='y'">
                <input type="text" class="form-control input-sm" data-toggle="tooltip" title="Indique la cédula de identidad" placeholder="Cédula de Identidad" v-model="person.id_number">
              </div>
              <div v-if="errors.people[index].id_number">
                <div class="alert alert-danger" v-if="errors.people[index].id_number.length > 0">
                  <ul>
                    <li v-for="error in errors.people[index].id_number">{{ error }}</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
          <div class="col-xl-3 col-lg-3 col-md-3 col-sm-3">
            <div class="form-group ">
              <input type="email" class="form-control input-sm" data-toggle="tooltip" title="Indique el correo electrónico" placeholder="Correo Electrónico" v-model="person.email">
            </div>
            <div v-if="errors.people[index].email">
              <div class="alert alert-danger" v-if="errors.people[index].email.length > 0">
                <ul>
                  <li v-for="error in errors.people[index].email">{{ error }}</li>
                </ul>
              </div>
            </div>
          </div>
          <div class="col-xl-3 col-lg-3 col-md-3 col-sm-3">
            <div class="form-group ">
              <input type="text" class="form-control input-sm" data-toggle="tooltip" title="Indique el número telefónico" placeholder="Número Telefónico" v-model="person.phone">
            </div>
            <div v-if="errors.people[index].phone">
              <div class="alert alert-danger" v-if="errors.people[index].phone.length > 0">
                <ul>
                  <li v-for="error in errors.people[index].phone">{{ error }}</li>
                </ul>
              </div>
            </div>
          </div>
          <div class="col-xl-3 col-lg-3 col-md-3 col-sm-3">
            <div class="form-group ">
              <label class="control-label" for="">
                Tipo de Voto:
              </label>
              <select2 :options="vote_types"
                v-model="person.vote_type_id">
              </select2>
            </div>
            <div v-if="errors.people[index].vote_type_id">
              <div class="alert alert-danger" v-if="errors.people[index].vote_type_id.length > 0">
                <ul>
                  <li v-for="error in errors.people[index].vote_type_id">{{ error }}</li>
                </ul>
              </div>
            </div>
          </div>
          <div class="col-xl-3 col-lg-3 col-md-3 col-sm-3">
            <div class="form-group ">
              <label class="control-label" for="">
                Parentesco:
              </label>
              <select2 :options="relationships"
                v-model="person.relationship_id">
              </select2>
            </div>
            <div v-if="errors.people[index].relationship_id">
              <div class="alert alert-danger" v-if="errors.people[index].relationship_id.length > 0">
                <ul>
                  <li v-for="error in errors.people[index].relationship_id">{{ error }}</li>
                </ul>
              </div>
            </div>
          </div>
          <div class="col-xl-3 col-lg-3 col-md-3 col-sm-3">
            <div class="form-group">
              <label class="control-label" for="">
                ¿Jefe Familiar?
              </label>
              <input type="checkbox" v-model="person.family_head">
            </div>
          </div>
          <div class="col-xl-1 col-lg-1 col-md-1 col-sm-1">
            <div class="form-group">
              <button class="btn btn-sm btn-danger btn-action" type="button"
                @click="deletePerson(index, record.people)"
                title="Eliminar este dato" data-toggle="tooltip" data-placement="right">
                <i class="fa fa-minus-circle"></i>
              </button>
            </div>
          </div>
        </div>

      </div>
      <div class="card-footer small text-right">
        <button type="button" class="btn btn-primary btn-sm" data-toggle="tooltip" @click="reset">Limpiar</button>
        <button type="submit" class="btn btn-primary btn-sm" data-toggle="tooltip" @click="createRecord(url)">Registrar</button>
      </div>
    <!--</form>-->
  </div>
  `
});
