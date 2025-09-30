/// Res_hel boite de dialogue pour réseau hélicoïdal

res_hel:dialog{
  label="Réseau hélicoïdal";
  initial_focus="nbre";
  spacer;
  :row{
    :edit_box{
      label="Nombre d'éléments";
      key="nbre";
      edit_width=8;
    }
    spacer;
    :button{
      label="Choix des objets";
      key="jeu_sel";
      fixed_width=true;
    }
  }
  spacer;
  :boxed_row{
    label="Centre du réseau";
    :edit_box{
      label="X :";
      key="x_coord";
      edit_width=12;
    }
    spacer;
    :edit_box{
      label="Y :";
      key="y_coord";
      edit_width=12;
    }
    spacer;
    :button{
      label=">>";
      key="cen_sel";
      fixed_width=true;
      height=2;
    }
  }
  spacer;
  :boxed_row{
  label="Décalage en hauteur";
    :popup_list{
      key="dec_ht";
      width=22;
    }
    :edit_box{
      key="ht_clv";
      edit_width=12;
    }
    spacer;
    :button{
      label=">>";
      key="ht_sel";
      fixed_width=true;
      height=2;
    }
  }
  spacer;
  :boxed_column{
    label="Rotation";
    :radio_row{
      :radio_button{
        label="Sens trigonométrique";
        key="tri";
      }
      :radio_button{
        label="Sens horaire";
        key="hor";
      }
    }
    :row{
      :popup_list{
        key="ang_typ";
        width=22;
      }
      :edit_box{
        key="ang_clv";
        edit_width=12;
      }
      spacer;
      :button{
        label=">>";
        key="ang_sel";
        fixed_width=true;
        height=2;
      }
    }
  }
  spacer;
  ok_cancel;
}