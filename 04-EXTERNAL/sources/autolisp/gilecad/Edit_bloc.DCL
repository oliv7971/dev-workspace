// Boite de dialogue du LISP EDIT_BLOC version 3.3
edit_bloc_3:dialog{
  label="Redéfinition de blocs";
  :boxed_row{
    label="Choix des blocs";
    :radio_column{
      :radio_button{
        label="Toute la collection";
        key="tbl";
        fixed_width=true;
        allow_accept=true;
      }
      :radio_button{
        label="Tous les blocs insérés";
        key="all";
        fixed_width=true;
        allow_accept=true;
      }
      :radio_button{
        label="Sélection";
        key="sel";
        value="1";
        fixed_width=true;
      }
    }
    :button{
      label=" >> ";
      key="ss";
      fixed_width=true;
      alignment=bottom;
      allow_accept=true;
    }
  }
  :boxed_column{
    label="Propriétés à modifier";
    :row{
      :toggle{
        label= "Échelle globale";
        key="scl";
        value="0";
      }
      :edit_box{
        key="fact";
        edit_width=8;
        value="1.0";
        allow_accept=true;
      }
    }
    spacer;
    :popup_list{
      label="Unités ";
      key="unt";
      edit_width=16;
    }
    spacer;
    :row{
      :column{
        :toggle{
          label="Calque";
          key="lay";
          fixed_width=true;
          allow_accept=true;
        }
        spacer_1;
        :toggle{
          label="Couleur";
          key="col";
          fixed_width=true;
          allow_accept=true;
        }
        spacer_1;
        :toggle{
          label="Type de ligne";
          key="tl";
          fixed_width=true;
          allow_accept=true;
        }
        :toggle{
          label="Epaisseur de ligne";
          key="el";
          fixed_width=true;
          allow_accept=true;
        }
        :toggle{
          label="Style de tracé";
          key="plt";
          fixed_width=true;
          allow_accept=true;
        }
      }
      :column{
        :popup_list{
          key="lay_l";
          alignment=right;
        }
        spacer_1;
        :column{
          :row{
            :image{
              key="i_col";
              width=1;
              height=1;
              aspect_ratio=1.0;
            }
            :text{
              key="t_col";
              width=20;
            }
          }
          :row{
            :toggle{
              label="DuBloc";
              key="col_db";
              value="1";
            }
            :button{
              label="Autres...";
              key="col_s";
              fixed_width=true;
              alignment=right;
            }
          }
        }
        :popup_list{
          key="tl_l";
          alignment=right;
        }
        :popup_list{
          key="el_l";
          alignment=right;
        }
        :radio_row{
          key="plt_r";
          :radio_button{
            label="DuBloc";
            key="plt_db";
            value="1";
          }
          :radio_button{
            label="DuCalque";
            key="plt_dc";
          }
        }
      }
    }
  }
  spacer;
  ok_cancel;
}

// Boite de dialogue Echelle des blocs dynamiques
alert_bloc:dialog{
  label="Échelle des blocs dynamiques";
  :paragraph{
    :text_part{
      value="Le changement d'échelle n'affecte pas";
    }
    :text_part{
      value="les paramètres des blocs dynamiques.";
    }
  }
  spacer;
  :boxed_column{
    label="Modifier l'échelle du bloc";
    :text{ 
      key="txt";
    }
    :radio_row{
      :radio_button{
        label="Oui";
        mnemonic="O";
        key="mod";
      }
      :radio_button{
        label="Non";
        mnemonic="N";
        key="anl";
        value="1";
      }
    }
  }
  ok_only;
}